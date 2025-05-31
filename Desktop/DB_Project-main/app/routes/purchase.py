from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from config import templates
import database

router = APIRouter()

@router.get("/purchase", response_class=HTMLResponse)
async def show_purchase_plan(request: Request):
    return templates.TemplateResponse("purchase.html", {"request": request})


@router.get("/checkout", response_class=HTMLResponse)
async def show_checkout_page(request: Request):
    return templates.TemplateResponse("checkout.html", {"request": request})


@router.post("/purchase-premium")
async def purchase_premium(data: dict):
    username = data.get("username")
    if not username:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

    user = await database.db.users.find_one({"username": username})
    if not user:
        return JSONResponse(status_code=404, content={"detail": "User not found"})

    await database.db.users.update_one(
        {"username": username},
        {"$set": {"is_premium": True}}
    )

    return {"message": "User upgraded to premium"}
