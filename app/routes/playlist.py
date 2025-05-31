from fastapi import APIRouter, Query, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import HTMLResponse
from config import templates
import database
from typing import Dict, Any, Optional
from bson import ObjectId
from mutagen import File as MutagenFile
import os


router = APIRouter()


@router.get("/playlist", response_class=HTMLResponse)
async def show_playlist_page(request: Request):
    return templates.TemplateResponse("playlist.html", {"request": request})


@router.get("/api/playlist")
async def get_playlist(
    name: str = Query(...), user: str = Query(...)
) -> Dict[str, Any]:
    # Find the user by username
    user_doc = await database.db["users"].find_one({"username": user})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    username = user_doc["username"]

    # Find the playlist by name and username
    playlist_doc = await database.db["playlists"].find_one(
        {"name": name, "username": username}
    )
    if not playlist_doc:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Expand items if needed (e.g. fetch full song metadata)
    items = []
    for item in playlist_doc.get("items", []):
        if isinstance(item, str):
            # Try to fetch song or podcast details by ID (optional enhancement)
            song_doc = await database.db["songs"].find_one({"_id": ObjectId(item)})
            if song_doc:
                items.append(
                    {
                        "title": song_doc.get("title", "Unknown"),
                        "artist": song_doc.get("artist", "Unknown"),
                        "genre": song_doc.get("genre", "Unknown"),
                        "duration": song_doc.get("duration", "0:00"),
                        "file_url": f"/static/musics/{username}/{song_doc.get('title')}.mp3",  # assuming .mp3 and title-based filenames
                    }
                )
            else:
                items.append(
                    {"title": "Unknown", "artist": "Unknown", "duration": "0:00"}
                )

        elif isinstance(item, dict):
            items.append(item)

    # Determine image file path on disk (adjust the base directory as needed)
    base_static_path = "static/images/playlists"
    image_filename = f"{username}_{name}.jpg"
    image_path = os.path.join(base_static_path, image_filename)

    if os.path.exists(image_path):
        image_url = f"/static/images/playlists/{image_filename}"
    else:
        image_url = "/static/images/playlists/playlist_default.jpg"

    return {
        "name": playlist_doc["name"],
        "username": user,
        "type": playlist_doc.get("type", "song"),
        "description": playlist_doc.get("description", ""),
        "items": items,
        "artists": list({item["artist"] for item in items if "artist" in item}),
        "release": f"Uploaded at ...",
        "image_url": image_url,
    }


@router.post("/api/playlist/{username}/{playlist_name}/add-song")
async def add_song_to_playlist(
    username: str,
    playlist_name: str,
    name: str = Form(...),
    artist: str = Form(...),
    lyrics: Optional[str] = Form(None),
    play_count: int = Form(0),
    genre: Optional[str] = Form(None),
    song_file: UploadFile = File(...),  # <-- removed duration from form
):
    playlist = await database.db["playlists"].find_one(
        {"username": username, "name": playlist_name}
    )
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    upload_dir = os.path.join("static", "musics", username)
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(song_file.filename)[1]
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).rstrip()
    filename = f"{safe_name}{file_ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        content = await song_file.read()
        buffer.write(content)

    # ✅ Auto-extract duration from the uploaded file
    audio = MutagenFile(file_path)
    if audio is None or not hasattr(audio, "info") or not hasattr(audio.info, "length"):
        duration = 0.0
    else:
        duration = round(audio.info.length, 2)

    new_song = {
        "username": username,
        "title": name,
        "artist": artist,
        "lyrics": lyrics,
        "play_count": play_count,
        "genre": genre,
        "duration": duration,
    }

    # Insert new song to DB
    result = await database.db["songs"].insert_one(new_song)
    new_song_id = result.inserted_id

    # Add song reference to playlist
    playlist["items"].append(str(new_song_id))
    await database.db["playlists"].update_one(
        {"_id": playlist["_id"]}, {"$set": {"items": playlist["items"]}}
    )

    new_song["_id"] = str(new_song_id)
    return JSONResponse({"message": "Song added successfully", "song": new_song})
