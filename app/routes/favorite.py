from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from config import templates
import shutil, os
import schemas, database
from urllib.parse import unquote


router = APIRouter()


@router.get("/favorite", response_class=HTMLResponse)
async def show_playlist_page(request: Request):
    return templates.TemplateResponse("favorite.html", {"request": request})


# this is called from playlist.js
@router.post("/api/favorite")
async def add_to_favorite(data: schemas.FavoriteRequest):
    STATIC_MUSIC_PATH = "static/musics"
    user_dir = os.path.join(STATIC_MUSIC_PATH, data.username)
    source_song_path = os.path.join(user_dir, f"{data.title}.mp3")

    favorite_folder = os.path.join(user_dir, "favorite")
    os.makedirs(favorite_folder, exist_ok=True)  # create if not exist

    destination_song_path = os.path.join(favorite_folder, f"{data.title}.mp3")

    if not os.path.exists(source_song_path):
        raise HTTPException(status_code=404, detail="Song file not found.")

    if not os.path.exists(destination_song_path):
        shutil.copy2(source_song_path, destination_song_path)

    # ✅ Update the user's favorite_items list in MongoDB
    user = await database.db.users.find_one({"username": data.username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    await database.db.users.update_one(
        {"username": data.username},
        {"$addToSet": {"favorite_items": f"{data.title}"}},  # prevents duplicates
    )

    return {"message": "Song added to favorites."}


def convert_objectid(song):
    song["_id"] = str(song["_id"])
    return song


@router.get("/api/favorites/{username}")
async def get_user_favorites(username: str):
    user = await database.db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    favorite_titles = user.get("favorite_items", [])
    songs_cursor = database.db.songs.find({"title": {"$in": favorite_titles}})
    songs_raw = await songs_cursor.to_list(length=None)

    songs = [convert_objectid(song) for song in songs_raw]

    return songs


@router.delete("/api/favorites/{username}/{title}")
async def remove_favorite(username: str, title: str):
    title = unquote(title)

    user = await database.db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Remove song title from favorite_items
    await database.db.users.update_one(
        {"username": username}, {"$pull": {"favorite_items": title}}
    )

    # Remove song file from favorite folder
    fav_path = f"./static/musics/{username}/favorite/{title}.mp3"
    if os.path.exists(fav_path):
        os.remove(fav_path)

    return {"detail": "Song removed from favorites"}
