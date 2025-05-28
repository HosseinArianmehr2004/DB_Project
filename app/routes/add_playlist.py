from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from config import templates
import database
import json
import os
from PIL import Image as pil_image
import io


router = APIRouter()


@router.get("/add_playlist", response_class=HTMLResponse)
async def add_playlist(request: Request):
    return templates.TemplateResponse("add_playlist.html", {"request": request})


@router.get("/api/user_playlists")
async def get_user_playlists(username: str):
    playlists = []
    cursor = database.db.playlists.find({"username": username})
    async for playlist in cursor:
        playlist["_id"] = str(playlist["_id"])  # convert ObjectId to string if needed
        playlists.append(playlist)
    return JSONResponse(content=playlists)


@router.post("/api/create_playlist")
async def create_playlist(
    username: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    items: str = Form("[]"),
    image: UploadFile = File(None),
):
    # Check for existing playlist with same name for user
    existing = await database.db.playlists.find_one(
        {"username": username, "name": name}
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Playlist with this name already exists."
        )

    # Save uploaded image if any, resize to 240x240
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        safe_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_user = "".join(
            c for c in username if c.isalnum() or c in ("@", ".", "-", "_")
        ).rstrip()
        filename = f"{safe_user}_{safe_name}{file_ext}"
        save_dir = os.path.join("static", "images", "playlists")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        # Read image bytes from UploadFile
        contents = await image.read()
        img = pil_image.open(io.BytesIO(contents))

        # Resize image to 240x240, keep aspect ratio or force exact size?
        # Here we force exact size (can distort), use img.thumbnail() for aspect ratio
        img = img.resize((240, 240))

        # Save resized image to disk
        img.save(save_path)

    try:
        items_list = json.loads(items)
    except:
        items_list = []

    playlist_dict = {
        "username": username,
        "name": name,
        "description": description,
        "items": items_list,
    }

    result = await database.db.playlists.insert_one(playlist_dict)

    return {
        "message": "Playlist created successfully.",
        "id": str(result.inserted_id),
    }
