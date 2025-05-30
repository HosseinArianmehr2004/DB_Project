from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/album", response_class=HTMLResponse)
async def get_albums(request: Request):
    logger.info("Starting /album route")
    try:
        logger.info("Testing database connection...")
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        logger.info("Fetching featured albums...")
        featured_albums = await database.db.albums.find({"featured": True}).to_list(length=10) or []
        logger.info(f"Found {len(featured_albums)} featured albums")

        logger.info("Fetching trending albums...")
        trending_albums = await database.db.albums.find({"trending": True}).to_list(length=10) or []
        logger.info("Fetching top albums...")
        top_albums = await database.db.albums.find().sort("plays", -1).to_list(length=15) or []
        logger.info("Fetching artists...")
        artists = await database.db.artists.find().to_list(length=10) or []
        logger.info("Fetching new albums...")
        new_albums = await database.db.albums.find().sort("release_date", -1).to_list(length=5) or []
        logger.info("Fetching radio stations...")
        radio_stations = await database.db.stations.find().to_list(length=10) or []
        logger.info("Fetching trending songs...")
        trending_songs = await database.db.songs.find({"trending": True}).to_list(length=5) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("album.html", {
            "request": request,
            "featured_albums": featured_albums,
            "trending_albums": trending_albums,
            "top_albums": top_albums,
            "artists": artists,
            "new_albums": new_albums,
            "radio_stations": radio_stations,
            "trending_songs": trending_songs
        })
    except Exception as e:
        logger.error(f"Error in /album route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)