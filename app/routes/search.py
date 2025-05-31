from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from config import templates
import database
import re


router = APIRouter()


@router.get("/api/search-songs")
async def search_songs(q: str = Query(..., min_length=1)):
    regex = {"$regex": re.escape(q), "$options": "i"}  # case-insensitive search
    songs_cursor = database.db["songs"].find(
        {"$or": [{"title": regex}, {"artist": regex}]}
    )

    songs = []
    async for song in songs_cursor:
        song["_id"] = str(song["_id"])
        songs.append(song)

    return JSONResponse(content={"results": songs})
