from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from config import templates
import database
import re


router = APIRouter()


@router.get("/genres", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("genres.html", {"request": request})


@router.get("/api/genre-songs")
async def get_songs_by_genre(genre: str):
    songs_cursor = database.db["songs"].find(
        {"genre": {"$regex": genre, "$options": "i"}}
    )
    songs = []
    async for song in songs_cursor:
        username = song.get("username", "unknown")
        title = song.get("title", "Unknown")

        songs.append(
            {
                "title": title,
                "artist": song.get("artist", "Unknown"),
                "genre": song.get("genre", "Unknown"),
                "duration": song.get("duration", "0:00"),
                "username": username,  # ✅ Add this line
                "file_url": f"/static/musics/{username}/{title}.mp3",
            }
        )

    return JSONResponse(content={"songs": songs})
