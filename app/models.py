from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from datetime import date, datetime


class User(BaseModel):
    username: Optional[str] = None
    password: str
    email: EmailStr
    is_premium: bool = False
    name: Optional[str] = None
    # lastname: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    # credit_card: Optional[str] = None
    profile_image: Optional[str] = None


class Song(BaseModel):
    url: str
    title: str
    artist: str
    lyrics: Optional[str] = None
    play_count: int = 0
    genre: Optional[str] = None
    duration: float  # in seconds


class Podcast(BaseModel):
    url: str
    title: str
    host: str
    description: Optional[str] = None
    play_count: int = 0
    genre: Optional[str] = None
    duration: float


class Favorite(BaseModel):
    user_id: str  # Foreign key (username or MongoDB _id)
    items: List[Union[str, dict]] = []  # List of song or podcast IDs


class Playlist(BaseModel):
    user_id: str  # Link to user
    name: str
    items: List[Union[str, dict]] = []  # Song/Podcast IDs


class SearchEntry(BaseModel):
    user_id: str
    query: str
    timestamp: datetime


