import React, { useState } from "react";

function CreatePlaylist({ moods, setMoods }) {
  const [moodName, setMoodName] = useState("");
  const [songName, setSongName] = useState("");

  const addMood = () => {
    if (!moodName || !songName) return alert("Please fill both fields!");
    const newMood = { name: moodName, songs: [songName] };
    setMoods([...moods, newMood]);
    setMoodName("");
    setSongName("");
  };

  return (
    <div className="page">
      <h2>Create a New Playlist</h2>
      <input
        type="text"
        placeholder="Mood name"
        value={moodName}
        onChange={(e) => setMoodName(e.target.value)}
      />
      <input
        type="text"
        placeholder="Song name"
        value={songName}
        onChange={(e) => setSongName(e.target.value)}
      />
      <button onClick={addMood}>Add Playlist</button>
    </div>
  );
}

export default CreatePlaylist;
