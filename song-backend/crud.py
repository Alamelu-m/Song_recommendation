from sqlalchemy.orm import Session
import models, schemas
import random

# ---------------- SONG CRUD ----------------
def get_random_songs(db: Session, limit: int = 10):
    songs = db.query(models.Song).all()
    return random.sample(songs, min(len(songs), limit))

def create_song(db: Session, song: schemas.SongCreate, mood_id: int = None):
    db_song = models.Song(**song.dict(), mood_id=mood_id)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def create_songs_bulk(db: Session, songs: list[schemas.SongCreate], mood_id: int = None):
    db_songs = []
    for song in songs:
        db_song = models.Song(title=song.title, artist=song.artist, url=song.url, mood_id=mood_id)
        db.add(db_song)
        db_songs.append(db_song)
    db.commit()
    for db_song in db_songs:
        db.refresh(db_song)
    return db_songs

def get_song_by_url(db: Session, url: str):
    return db.query(models.Song).filter(models.Song.url == url).first()

def update_song(db: Session, song_id: int, song: schemas.SongCreate):
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not db_song:
        return None
    db_song.title = song.title
    db_song.artist = song.artist
    db_song.url = song.url
    db.commit()
    db.refresh(db_song)
    return db_song

def delete_song(db: Session, song_id: int):
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not db_song:
        return None
    db.delete(db_song)
    db.commit()
    return db_song


def get_moods(db: Session):
    return db.query(models.Mood).all()

def get_mood(db: Session, mood_id: int):
    return db.query(models.Mood).filter(models.Mood.id == mood_id).first()

def create_mood(db: Session, mood: schemas.MoodCreate):
    db_mood = models.Mood(name=mood.name)
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)

    if mood.songs:
        create_songs_bulk(db, mood.songs, mood_id=db_mood.id)

    return db_mood

def update_mood(db: Session, mood_id: int, name: str):
    db_mood = db.query(models.Mood).filter(models.Mood.id == mood_id).first()
    if not db_mood:
        return None
    db_mood.name = name
    db.commit()
    db.refresh(db_mood)
    return db_mood

def delete_mood(db: Session, mood_id: int):
    db_mood = db.query(models.Mood).filter(models.Mood.id == mood_id).first()
    if not db_mood:
        return None
    db.delete(db_mood)
    db.commit()
    return db_mood

def add_song(db: Session, mood_id: int, song: schemas.SongCreate):
    return create_song(db, song, mood_id=mood_id)

# ---------------- SEARCH ----------------
def search_moods(db: Session, query: str, search_type: str = "song"):
    if search_type == "song":
        return db.query(models.Song).filter(models.Song.title.ilike(f"%{query}%")).all()
    else:
        return db.query(models.Mood).filter(models.Mood.name.ilike(f"%{query}%")).all()



