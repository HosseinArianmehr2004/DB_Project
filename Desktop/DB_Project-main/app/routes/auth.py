from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import JWTError, jwt
from datetime import datetime, timedelta
import schemas, models, security, database
from typing import Dict
import logging  # Import logging module

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

# JWT Configuration
SECRET_KEY = "your-secret-key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.error("No email found in token payload")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError: {str(e)}")
        raise credentials_exception

    logger.info(f"Looking up user with email: {email}")
    user = await database.db.users.find_one({"email": email})
    if user is None:
        logger.error(f"User not found for email: {email}")
        raise credentials_exception
    # Convert _id to string to avoid ObjectId issues
    user["_id"] = str(user["_id"])
    logger.info(f"User found: {user['email']}")
    return user

@router.get("/get_username")
async def get_username(email: str):
    user = await database.db.users.find_one({"email": email})
    if not user or "username" not in user:
        raise HTTPException(status_code=404, detail="Username not found.")
    return {"username": user["username"]}

@router.post("/register")
async def register_user(user: models.User):
    existing_user = await database.db.users.find_one(
        {"$or": [{"email": user.email}, {"username": user.username}]}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    salt = security.generate_salt()
    hashed_password = security.hash_password(user.password, salt)

    user_data = user.dict()
    user_data["password"] = f"{salt}${hashed_password}"

    result = await database.db.users.insert_one(user_data)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}

@router.post("/login")
@limiter.limit("3/minute")
async def login_user(request: Request, credentials: schemas.LoginRequest):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await database.db.users.find_one({"email": credentials.email})
    if not user:
        raise auth_error

    try:
        salt, stored_hash = user["password"].split("$")
    except ValueError:
        raise auth_error

    input_hashed_password = security.hash_password(credentials.password, salt)
    if input_hashed_password != stored_hash:
        raise auth_error

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}