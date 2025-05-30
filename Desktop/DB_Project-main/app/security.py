from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime, timedelta
from jose import jwt, JWTError
import hashlib
import os
import base64
from fastapi import HTTPException, status
from security_config import (
    SECRET_KEY,
    PEPPER,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha512((password + salt + PEPPER).encode()).hexdigest()


def generate_salt() -> str:
    return base64.urlsafe_b64encode(os.urandom(16)).decode()


def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create access token: {str(e)}",
        )


def encrypt_data(plain_text: str, key: bytes) -> str:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(plain_text.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode()


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    data = base64.b64decode(encrypted_data)
    iv = data[:16]
    ct = data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return (decryptor.update(ct) + decryptor.finalize()).decode()
