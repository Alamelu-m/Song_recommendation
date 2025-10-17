import React from "react";

function ViewPlaylist({ moods, setMoods }) {
  const deleteMood = (index) => {
    const updated = moods.filter((_, i) => i !== index);
    setMoods(updated);
  };

  return (
    <div className="page">
      <h2>View All Playlists</h2>
      {moods.length === 0 ? (
        <p>No playlists yet.</p>
      ) : (
        moods.map((m, i) => (
          <div key={i} className="mood-box">
            <h3>{m.name}</h3>
            <ul>
              {m.songs.map((s, j) => (
                <li key={j}>{s}</li>
              ))}
            </ul>
            <button onClick={() => deleteMood(i)}>Delete</button>
          </div>
        ))
      )}
    </div>
  );
}

export default ViewPlaylist;
