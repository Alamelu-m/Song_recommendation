import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

function MoodPage() {
  const { moodName } = useParams();
  const [mood, setMood] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/moods/`)
      .then((res) => res.json())
      .then((data) => {
        const selectedMood = data.find((m) => m.name === moodName);
        setMood(selectedMood);
      });
  }, [moodName]);

  if (!mood) return <p>Loading...</p>;

  const filteredSongs = mood.songs
    .filter((s) => s.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 15); 

  return (
    <div className="mood-page">
      <h1>{mood.name} Mood 🎵</h1>

      <input
        type="text"
        placeholder="Search songs..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <ul>
        {filteredSongs.length === 0 ? (
          <p>No songs found</p>
        ) : (
          filteredSongs.map((song, i) => <li key={i}>{song}</li>)
        )}
      </ul>
    </div>
  );
}

export default MoodPage;
