from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
import schemas, models, security, database


router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


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

    # Generate salt and hash password
    salt = security.generate_salt()
    hashed_password = security.hash_password(user.password, salt)

    # Prepare user data with hashed password
    user_data = user.dict()
    user_data["password"] = f"{salt}${hashed_password}"

    # Insert into the database
    result = await database.db.users.insert_one(user_data)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}


@router.post("/login")
@limiter.limit("3/minute")  # 3 sequential wrong password per minute
# async def login_user(credentials: schemas.LoginRequest):
async def login_user(request: Request, credentials: schemas.LoginRequest):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Find user by email
    user = await database.db.users.find_one({"email": credentials.email})
    if not user:
        raise auth_error

    # 2. Extract salt and stored hash
    try:
        salt, stored_hash = user["password"].split("$")
    except ValueError:
        raise auth_error  # corrupted or invalid password format

    # 3. Hash the input password with the extracted salt
    input_hashed_password = security.hash_password(credentials.password, salt)
    if input_hashed_password != stored_hash:
        raise auth_error

    # 4. (Optional) Generate JWT token and return it
    return {"message": "Login successful"}
