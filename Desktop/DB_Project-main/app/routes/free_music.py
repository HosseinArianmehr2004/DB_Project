from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/free_music", response_class=HTMLResponse)
async def get_free_music(request: Request):
    logger.info("Starting /free_music route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch trending tracks, albums, and latest tracks
        trending_tracks = await database.db.songs.find({"trending": True}).to_list(length=10) or []
        logger.info(f"Found {len(trending_tracks)} trending tracks")
        free_albums = await database.db.albums.find({"free": True}).to_list(length=10) or []
        logger.info(f"Found {len(free_albums)} free albums")
        latest_tracks = await database.db.songs.find().sort("release_date", -1).limit(10).to_list() or []
        logger.info(f"Found {len(latest_tracks)} latest tracks")
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("free_music.html", {
            "request": request,
            "trending_tracks": trending_tracks,
            "free_albums": free_albums,
            "latest_tracks": latest_tracks,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /free_music route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)