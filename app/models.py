from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union, Literal
from datetime import date, datetime


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    is_premium: bool = False
    name: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    # credit_card: Optional[str] = None
    favorite_items: List[str] = [] # sontain Songs


class Song(BaseModel):
    title: str
    artist: str
    lyrics: Optional[str] = None
    play_count: int = 0
    genre: Optional[str] = None
    duration: float  # in seconds


# class Podcast(BaseModel):
#     name: str
#     host: str
#     description: Optional[str] = None
#     play_count: int = 0
#     genre: Optional[str] = None
#     duration: float


# class Favorite(BaseModel):
#     user_id: str  # Foreign key (username or MongoDB _id)
#     items: List[Union[str, dict]] = []  # List of song or podcast IDs


# class Favorite(BaseModel):
#     user_id: str  # Foreign key (username or MongoDB _id)
#     items: List[str] = [] # sontain Songs


class Playlist(BaseModel):
    username: str
    name: str
    description: Optional[str] = None
    # type: Literal["song", "podcast"] = "song"
    items: List[Union[str, dict]] = []


class SearchEntry(BaseModel):
    user_id: str
    query: str
    timestamp: datetime
