from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import templates
from bson import ObjectId
import database
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/stations", response_class=HTMLResponse)
async def get_stations(request: Request):
    logger.info("Starting /stations route")
    try:
        # Test database connection
        await database.client.admin.command("ping")
        logger.info("Database connection successful")

        # Fetch live stations and live radio
        live_stations = await database.db.stations.find().sort("frequency", 1).to_list(length=10) or []
        logger.info(f"Found {len(live_stations)} live stations")
        live_radio = await database.db.stations.find().to_list(length=10) or []

        logger.info("Rendering template...")
        return templates.TemplateResponse("stations.html", {
            "request": request,
            "live_stations": live_stations,
            "live_radio": live_radio
        })
    except Exception as e:
        logger.error(f"Error in /stations route: {str(e)}")
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)