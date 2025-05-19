from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Body,
    UploadFile,
    File,
    Form,
    status,
)
from fastapi.responses import HTMLResponse
from pathlib import Path
from config import templates
import database, schemas
import shutil


router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/get-profile")
async def get_profile(email: str):
    user = await database.db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    return user


@router.post("/update-profile")
async def update_profile(data: dict = Body(...)):
    email = data.get("email")
    new_username = data.get("username")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # Ensure new username is unique
    if new_username:
        existing_user = await database.db.users.find_one(
            {"username": new_username, "email": {"$ne": email}}
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

    update_data = {k: v for k, v in data.items() if k != "email"}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await database.db.users.update_one({"email": email}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    if result.modified_count == 0:
        return {"message": "No changes made"}

    return {"message": "Profile updated successfully"}


@router.post("/upload-profile-image")
async def upload_profile_image(image: UploadFile = File(...), email: str = Form(...)):
    user = await database.db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    username = user.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required to upload a profile image. Please update your profile first.",
        )

    ext = Path(image.filename).suffix
    filename = f"{username}{ext}"
    upload_dir = Path("static/images/profiles")
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / filename

    with save_path.open("wb") as f:
        shutil.copyfileobj(image.file, f)

    image_url = f"/static/images/profiles/{filename}"

    await database.db.users.update_one(
        {"email": email}, {"$set": {"profile_image": image_url}}
    )

    return {"message": "Image uploaded", "image_url": image_url}
