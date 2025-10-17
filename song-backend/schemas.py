from pydantic import BaseModel, EmailStr,constr
from typing import List, Optional

class SongBase(BaseModel):
    title: str
    artist: str
    url: str
    mood_id: Optional[int] = None 

class SongCreate(SongBase):
    pass

class Song(SongBase):
    id: int


    class Config:
        from_attributes = True

class MoodBase(BaseModel):
    name: str

class MoodCreate(MoodBase):
    songs: List[SongCreate] = []

class Mood(MoodBase):
    id: int
    songs: List[Song] = []

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=72)

class UserLogin(BaseModel):
    username: str
    password: str

