from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging
from routes.auth import get_current_user  

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/favourites", response_class=HTMLResponse)
async def get_favourites(request: Request, current_user: dict = Depends(get_current_user)):
    logger.info("Starting /favourites route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch user by email (since token uses email)
        logger.info(f"Current user email: {current_user['email']}")
        user = await database.db.users.find_one({"email": current_user["email"]})
        if not user:
            logger.error(f"User not found for email: {current_user['email']}")
            raise HTTPException(status_code=404, detail="User not found in database")

        # Fetch favourite songs
        if "favourites" not in user or not user["favourites"]:
            logger.info("No favourites found for user")
            favourite_songs = []
        else:
            favourite_song_ids = [ObjectId(song_id) for song_id in user["favourites"]]
            favourite_songs = await database.db.songs.find({"_id": {"$in": favourite_song_ids}}).to_list(length=10) or []
        logger.info(f"Found {len(favourite_songs)} favourite songs")

        # Fetch recently played
        recently_played = await database.db.stations.find().to_list(length=10) or []
        logger.info(f"Found {len(recently_played)} recently played items")

        logger.info("Rendering template...")
        return templates.TemplateResponse("favourite.html", {
            "request": request,
            "favourite_songs": favourite_songs,
            "recently_played": recently_played
        })
    except HTTPException as he:
        logger.error(f"HTTPException: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error in /favourites route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")