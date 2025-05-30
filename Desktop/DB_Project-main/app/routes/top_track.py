from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/top_track", response_class=HTMLResponse)
async def get_top_track(request: Request):
    logger.info("Starting /top_track route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch weekly top 15 (sort by some metric, e.g., plays or rating, if available)
        weekly_top_15 = await database.db.songs.find().sort("plays", -1).limit(15).to_list(length=15) or []
        logger.info(f"Found {len(weekly_top_15)} weekly top 15 tracks")

        # Fetch top tracks of all time (e.g., highest rated or most played)
        top_tracks_all_time = await database.db.songs.find().sort("rating", -1).limit(10).to_list(length=10) or []
        logger.info(f"Found {len(top_tracks_all_time)} top tracks of all time")

        # Fetch trending tracks
        trending_tracks = await database.db.songs.find({"trending": True}).limit(5).to_list(length=5) or []
        logger.info(f"Found {len(trending_tracks)} trending tracks")

        # Fetch live radio stations
        live_radio = await database.db.stations.find().limit(10).to_list(length=10) or []
        logger.info(f"Found {len(live_radio)} live radio stations")

        logger.info("Rendering template...")
        return templates.TemplateResponse("top_track.html", {
            "request": request,
            "weekly_top_15": weekly_top_15,
            "top_tracks_all_time": top_tracks_all_time,
            "trending_tracks": trending_tracks,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /top_track route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)