from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random
import models, schemas, crud
from passlib.context import CryptContext
from database import Base, engine, get_db, SessionLocal
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from fastapi.middleware.cors import CORSMiddleware

# ----- Create tables -----
Base.metadata.create_all(bind=engine)

# ----- FastAPI App -----
app = FastAPI(title="Mood-Based Song Recommender 🎵")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Spotify Setup -----
client_id = "YOUR SPOTIFY ID"
client_secret = "YOUR SPOTIFY SECRET"
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username/email exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful!"}

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": f"Welcome {db_user.username}!"}



@app.get("/songs/", response_model=List[schemas.Song])
def read_songs(db: Session = Depends(get_db)):
    return db.query(models.Song).all()

@app.post("/songs/", response_model=schemas.Song)
def add_song(song: schemas.SongCreate, mood_id: int = None, db: Session = Depends(get_db)):
    return crud.create_song(db, song, mood_id)

@app.put("/songs/{song_id}", response_model=schemas.Song)
def edit_song(song_id: int, song: schemas.SongCreate, db: Session = Depends(get_db)):
    updated = crud.update_song(db, song_id, song)
    if not updated:
        raise HTTPException(status_code=404, detail="Song not found")
    return updated

@app.delete("/songs/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_song(db, song_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": "Song deleted successfully"}

@app.get("/random-songs/", response_model=List[schemas.Song])
def random_songs(db: Session = Depends(get_db), limit: int = 10):
    return crud.get_random_songs(db, limit=limit)


@app.get("/moods/", response_model=List[schemas.Mood])
def read_moods(db: Session = Depends(get_db)):
    return crud.get_moods(db)

@app.post("/moods/", response_model=schemas.Mood)
def create_mood(mood: schemas.MoodCreate, db: Session = Depends(get_db)):
  
    results = sp.search(q=mood.name, type="track", limit=5)
    mood.songs = [
        schemas.SongCreate(
            title=track["name"],
            artist=track["artists"][0]["name"],
            url=track["preview_url"] or ""
        )
        for track in results["tracks"]["items"] if track["preview_url"]
    ]
    return crud.create_mood(db, mood)

@app.put("/moods/{mood_id}", response_model=schemas.Mood)
def edit_mood(mood_id: int, mood: schemas.MoodBase, db: Session = Depends(get_db)):
    updated = crud.update_mood(db, mood_id, mood.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Mood not found")
    return updated

@app.delete("/moods/{mood_id}")
def delete_mood(mood_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_mood(db, mood_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mood not found")
    return {"message": "Mood deleted successfully"}

@app.post("/moods/{mood_id}/songs/", response_model=schemas.Song)
def add_song_to_mood(mood_id: int, song: schemas.SongCreate, db: Session = Depends(get_db)):
    mood = crud.get_mood(db, mood_id)
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return crud.add_song(db, mood_id, song)

@app.get("/search/")
def search(query: str, search_type: str = "song", db: Session = Depends(get_db)):
    return crud.search_moods(db, query, search_type)

@app.get("/spotify-songs/", response_model=List[schemas.Song])
def get_spotify_songs(mood: str = "happy", limit: int = 10):
    """
    Fetch playable preview songs from Spotify based on mood.
    """
    results = sp.search(q=mood, type="track", limit=limit)

    
    songs = [
        schemas.Song(
            id=i + 1,
            title=track["name"],
            artist=", ".join(artist["name"] for artist in track["artists"]),
            url=track["preview_url"],  
        )
        for i, track in enumerate(results["tracks"]["items"])
        if track["preview_url"]
    ]

    if not songs:
        raise HTTPException(status_code=404, detail="No playable songs found for this mood")

    return songs

@app.post("/fetch-and-store-songs/", response_model=List[schemas.Song])
def fetch_and_store_songs(mood: str = "happy", limit: int = 10, db: Session = Depends(get_db)):

    db_mood = db.query(models.Mood).filter(models.Mood.name == mood).first()
    if not db_mood:
        db_mood = models.Mood(name=mood)
        db.add(db_mood)
        db.commit()
        db.refresh(db_mood)

    results = sp.search(q=mood, type="track", limit=50)
    tracks_with_preview = [t for t in results["tracks"]["items"] if t["preview_url"]]

    if len(tracks_with_preview) < limit:
        # fallback to include tracks without preview_url
        tracks_with_preview += [t for t in results["tracks"]["items"] if t not in tracks_with_preview]

    random_tracks = random.sample(tracks_with_preview, min(limit, len(tracks_with_preview)))

    songs_to_store = [
        schemas.SongCreate(
            title=t["name"],
            artist=t["artists"][0]["name"],
            url=t["preview_url"] or t["external_urls"]["spotify"]
        )
        for t in random_tracks
    ]

    stored_songs = crud.create_songs_bulk(db, songs_to_store, mood_id=db_mood.id)
    return stored_songs






