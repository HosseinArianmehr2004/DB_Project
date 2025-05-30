from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from config import templates
import database
import logging
import os

# Define the router
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/download", response_class=HTMLResponse)
async def get_download(request: Request):
    logger.info("Accessing /download route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch free downloads (e.g., songs available for free download)
        free_downloads = await database.db.downloads.find().sort("number", 1).limit(10).to_list(10) or []
        logger.info(f"Found {len(free_downloads)} free downloads")

        # Fetch "Download Now" section (e.g., featured downloads)
        featured_downloads = await database.db.downloads.find({"featured": True}).limit(10).to_list(10) or []
        logger.info(f"Found {len(featured_downloads)} featured downloads")

        # Fetch "Recently Played" section (similar to history)
        recently_played = await database.db.history.find().sort("played_at", -1).limit(10).to_list(10) or []
        logger.info(f"Found {len(recently_played)} recently played tracks")

        logger.info("Rendering template...")
        return templates.TemplateResponse("download.html", {
            "request": request,
            "free_downloads": free_downloads,
            "featured_downloads": featured_downloads,
            "recently_played": recently_played
        })
    except Exception as e:
        logger.error(f"Error in /download route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/download/file")
async def download_file(track_title: str):
    logger.info(f"Starting /download/file route for track: {track_title}")
    try:
        # Fetch track details from database
        track = await database.db.downloads.find_one({"title": track_title})
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        # Assuming the file path is stored in the database or derived
        # For this example, we'll assume files are stored in a 'files' directory
        file_path = f"app/files/{track_title}.mp3"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        return FileResponse(file_path, media_type="audio/mpeg", filename=f"{track_title}.mp3")
    except Exception as e:
        logger.error(f"Error in /download/file route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")