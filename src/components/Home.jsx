import React, { useState, useEffect } from "react";
import axios from "axios";

function Home() {
  const [query, setQuery] = useState("");
  const [songs, setSongs] = useState([]);
  const [currentSong, setCurrentSong] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch random songs from DB on first load
  useEffect(() => {
    fetchRandomSongs();
  }, []);

  const fetchRandomSongs = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/random-songs/?limit=10");
      setSongs(res.data);
    } catch (err) {
      console.error("Error fetching random songs:", err);
    }
  };

  const searchSongs = async () => {
    if (!query.trim()) return fetchRandomSongs();

    setLoading(true);
    try {
      // 1️⃣ Try fetching from DB (mood-based search)
      const dbRes = await axios.get(`http://127.0.0.1:8000/moods/`);
      const mood = dbRes.data.find(
        (m) => m.name.toLowerCase() === query.toLowerCase()
      );

      if (mood && mood.songs.length > 0) {
        setSongs(mood.songs);
      } else {
        // 2️⃣ Fallback to Spotify API
        const spotifyRes = await axios.get(
          `http://127.0.0.1:8000/spotify-songs/?mood=${query}&limit=10`
        );
        setSongs(spotifyRes.data);
      }
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  const playSong = (song) => {
    if (!song.url) {
      alert("No preview available for this song");
      return;
    }
    setCurrentSong(song);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Mood-Based Song Recommender</h1>

      {/* Search Section */}
      <div style={{ margin: "20px 0" }}>
        <input
          type="text"
          placeholder="Search mood or song (e.g. happy, sad, chill)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ padding: "8px", width: "250px" }}
        />
        <button onClick={searchSongs} style={{ marginLeft: "10px", padding: "8px 15px" }}>
          Search
        </button>
      </div>

      {/* Songs Section */}
      <h2>{query ? `Results for "${query}"` : "🎶 Random Songs"}</h2>

      {loading ? (
        <p>Loading songs...</p>
      ) : songs.length === 0 ? (
        <p>No songs found.</p>
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "15px" }}>
          {songs.map((song, index) => (
            <div
              key={index}
              onClick={() => playSong(song)}
              style={{
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "10px",
                width: "200px",
                cursor: song.url ? "pointer" : "default",
                boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
              }}
            >
              <h3>{song.title}</h3>
              <p>{song.artist}</p>
            </div>
          ))}
        </div>
      )}

      {/* Audio Player */}
      {currentSong && (
        <div style={{ marginTop: "30px" }}>
          <h2>Now Playing: {currentSong.title}</h2>
          <audio controls autoPlay src={currentSong.url} style={{ width: "100%" }} />
        </div>
      )}
    </div>
  );
}

export default Home;




