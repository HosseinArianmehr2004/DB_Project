from dotenv import load_dotenv
import os
import base64


load_dotenv()  # Load environment variables from .env

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing SECRET_KEY")

PEPPER = os.getenv("PEPPER")
if not PEPPER:
    raise ValueError("Missing PEPPER")

MASTER_KEY = base64.b64decode(os.getenv("MASTER_KEY"))
if not MASTER_KEY:
    raise ValueError("Missing MASTER_KEY")
if len(MASTER_KEY) != 32:
    raise ValueError("MASTER_KEY must be 32 bytes for AES-256")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
