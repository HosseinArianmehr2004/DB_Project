from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/artist", response_class=HTMLResponse)
async def get_artists(request: Request):
    logger.info("Starting /artist route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch data with timeouts (5 seconds each)
        featured_artists = await database.db.artists.find({"featured": True}).to_list(length=10) or []
        logger.info(f"Found {len(featured_artists)} featured artists")
        top_artists = await database.db.artists.find().sort("plays", -1).to_list(length=15) or []
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("artist.html", {
            "request": request,
            "featured_artists": featured_artists,
            "top_artists": top_artists,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /artist route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@router.get("/artist_single", response_class=HTMLResponse)
async def get_artist_single(request: Request, artist_id: str = None):
    logger.info("Starting /artist_single route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch artist details
        artist = await database.db.artists.find_one({"_id": ObjectId(artist_id)}) if artist_id else None
        logger.info(f"Found artist: {artist}")

        # Fetch artist's songs
        songs = await database.db.songs.find({"artist": artist["name"]}).to_list(length=10) or []
        logger.info(f"Found {len(songs)} songs for artist")

        # Fetch similar artists (e.g., those with similar genres or popularity)
        similar_artists = await database.db.artists.find({"plays": {"$gt": 0}}).sort("plays", -1).limit(10).to_list() or []
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("artist_single.html", {
            "request": request,
            "artist": artist,
            "songs": songs,
            "similar_artists": similar_artists,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /artist_single route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)