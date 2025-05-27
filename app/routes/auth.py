from fastapi import APIRouter, HTTPException
import database, models, schemas


router = APIRouter()


@router.get("/get_username")
async def get_username(email: str):
    user = await database.db.users.find_one({"email": email})
    if not user or "username" not in user:
        raise HTTPException(status_code=404, detail="Username not found.")
    return {"username": user["username"]}


@router.post("/register")
async def register_user(user: models.User):
    # Check if username or email already exists
    existing_user = await database.db.users.find_one(
        {"$or": [{"email": user.email}, {"username": user.username}]}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    # Insert user into the database
    result = await database.db.users.insert_one(user.dict())
    return {"message": "User registered successfully", "id": str(result.inserted_id)}


@router.post("/login")
async def login_user(credentials: schemas.LoginRequest):
    user = await database.db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Replace with your password check logic
    if user["password"] != credentials.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Optionally generate JWT and return
    return {"message": "Login successful"}
