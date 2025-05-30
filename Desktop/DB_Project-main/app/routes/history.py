from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from config import templates
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/history", response_class=HTMLResponse)
async def get_history(request: Request):
    logger.info("Starting /history route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch recently played tracks (global history for all users or public data)
        history = await database.db.history.find().sort("played_at", -1).limit(10).to_list(10) or []
        logger.info(f"Found {len(history)} history entries")

        logger.info("Rendering template...")
        return templates.TemplateResponse("history.html", {
            "request": request,
            "history": history
        })
    except Exception as e:
        logger.error(f"Error in /history route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/history_single", response_class=HTMLResponse)
async def get_history_single(request: Request, track_title: str = None):
    logger.info("Starting /history_single route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch specific history entry by track title
        history_entry = await database.db.history.find_one({"title": track_title}) if track_title else None
        logger.info(f"Found history entry: {history_entry}")

        # Fetch related tracks (e.g., by the same artist)
        related_tracks = await database.db.history.find({"artist": history_entry["artist"]}).limit(10).to_list(10) or [] if history_entry else []
        logger.info(f"Found {len(related_tracks)} related tracks")

        logger.info("Rendering template...")
        return templates.TemplateResponse("history_single.html", {
            "request": request,
            "history_entry": history_entry,
            "related_tracks": related_tracks
        })
    except Exception as e:
        logger.error(f"Error in /history_single route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")