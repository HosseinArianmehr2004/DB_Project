from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/genres", response_class=HTMLResponse)
async def get_genres(request: Request):
    logger.info("Starting /genres route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch top genres and live radio
        top_genres = await database.db.genres.find().sort("popularity", -1).to_list(length=10) or []
        logger.info(f"Found {len(top_genres)} top genres")
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("genres.html", {
            "request": request,
            "top_genres": top_genres,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /genres route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@router.get("/genres_single", response_class=HTMLResponse)
async def get_genre_single(request: Request, genre_name: str = None):
    logger.info("Starting /genres_single route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch genre details
        genre = await database.db.genres.find_one({"name": genre_name}) if genre_name else None
        logger.info(f"Found genre: {genre}")

        # Fetch songs for the genre
        songs = await database.db.songs.find({"genre": genre_name}).to_list(length=10) or []
        logger.info(f"Found {len(songs)} songs for genre")

        # Fetch live radio (optional, for consistency)
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("genres_single.html", {
            "request": request,
            "genre": genre,
            "songs": songs,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /genres_single route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)