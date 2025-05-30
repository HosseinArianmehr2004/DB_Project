from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from config import templates
import logging
import database
from routes.auth import get_current_user  # Add this import

# Define the router
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/purchase", response_class=HTMLResponse)
async def get_purchase(request: Request, current_user: dict = Depends(get_current_user)):
    logger.info(f"Starting /purchase route for user: {current_user.get('email')}")
    try:
        return templates.TemplateResponse("purchase.html", {"request": request})
    except Exception as e:
        logger.error(f"Error in /purchase route: {str(e)}")
        raise HTTPException(status_code=500, detail="Server error")

@router.post("/purchase/premium")
async def process_premium_purchase(
    plan: str = Form(...),
    cardNumber: str = Form(...),
    expiryDate: str = Form(...),
    cvv: str = Form(...),
    name: str = Form(...),
    current_user: dict = Depends(get_current_user)  # Add dependency
):
    logger.info(f"Processing premium purchase for plan: {plan}, user: {current_user.get('email')}")
    try:
        # Simulate payment gateway validation
        if len(cardNumber) != 16 or not cardNumber.isdigit():
            raise ValueError("Invalid card number")
        if not expiryDate.replace("/", "").isdigit() or len(expiryDate) != 7:
            raise ValueError("Invalid expiry date")
        if len(cvv) != 3 or not cvv.isdigit():
            raise ValueError("Invalid CVV")

        # Simulate payment processing (in reality, call a payment gateway API here)
        logger.info("Payment validated successfully")
        # Update user database with premium status
        await database.db.users.update_one(
            {"email": current_user["email"]},
            {"$set": {"premium": plan}}
        )
        return JSONResponse({"message": f"Payment successful! You are now on {plan} plan."})
    except ValueError as e:
        logger.error(f"Payment validation failed: {str(e)}")
        return JSONResponse({"message": f"Payment failed: {str(e)}"}, status_code=400)
    except Exception as e:
        logger.error(f"Error in payment processing: {str(e)}")
        return JSONResponse({"message": "Payment failed: Server error"}, status_code=500)