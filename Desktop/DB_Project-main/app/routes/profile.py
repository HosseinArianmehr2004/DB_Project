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
import database
import shutil
import os
import re


router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/get-profile")
async def get_profile(username: str):
    user = await database.db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    return user


@router.post("/update-profile")
async def update_profile(data: dict = Body(...)):
    current_username = data.get("current_username")
    new_username = data.get("username")
    new_email = data.get("email")

    if not current_username:
        raise HTTPException(status_code=400, detail="Current username is required")

    user = await database.db.users.find_one({"username": current_username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    username_changed = False
    if new_username and new_username != current_username:
        if not re.match(r"^[a-zA-Z0-9_]{6,}$", new_username):
            raise HTTPException(
                status_code=400,
                detail="Username must be at least 6 characters and contain only letters, numbers, or underscores.",
            )
        existing_username = await database.db.users.find_one({"username": new_username})
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        username_changed = True
    else:
        data.pop("username", None)

    if new_email and new_email != user.get("email"):
        existing_email = await database.db.users.find_one({"email": new_email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already taken")

    update_data = {
        k: v
        for k, v in data.items()
        if k != "current_username" and v is not None and v != ""
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await database.db.users.update_one(
        {"username": current_username}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    if username_changed:
        # ✅ Rename playlist cover files
        playlist_dir = Path("static/images/playlists")
        for file in playlist_dir.glob(f"{current_username}_*.jpg"):
            new_name = file.name.replace(f"{current_username}_", f"{new_username}_", 1)
            new_path = playlist_dir / new_name
            os.rename(file, new_path)

        # ✅ Rename user profile image if it exists
        profile_image_dir = Path("static/images/profiles")
        old_profile_path = profile_image_dir / f"{current_username}.jpg"
        new_profile_path = profile_image_dir / f"{new_username}.jpg"
        if old_profile_path.exists():
            # ✅ Rename user profile image if it exists
            profile_image_dir = Path("static/images/profiles")
            old_profile_path = profile_image_dir / f"{current_username}.jpg"
            new_profile_path = profile_image_dir / f"{new_username}.jpg"
            if old_profile_path.exists():
                os.rename(old_profile_path, new_profile_path)

        # ✅ Update DB if necessary (optional)
        await database.db.playlists.update_many(
            {"username": current_username},
            {"$set": {"username": new_username}},
        )
        await database.db.playlists.update_many(
            {"cover_image": {"$regex": f"{current_username}_"}},
            [
                {
                    "$set": {
                        "cover_image": {
                            "$replaceOne": {
                                "input": "$cover_image",
                                "find": f"{current_username}_",
                                "replacement": f"{new_username}_",
                            }
                        }
                    }
                }
            ],
        )

    return {"message": "Profile updated successfully"}


@router.post("/upload-profile-image")
async def upload_profile_image(
    image: UploadFile = File(...), username: str = Form(...)
):
    user = await database.db.users.find_one({"username": username})
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

    # await database.db.users.update_one({"username": username})

    return {"message": "Image uploaded", "image_url": image_url}
