import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import MoodPage from "./components/MoodPage";
import CreatePlaylist from "./components/CreatePlaylist";
import ViewPlaylist from "./components/ViewPlaylist";
import Login from "./components/Login";
import Signup from "./components/Signup";
import axios from "axios";
import "./App.css";

function App() {
  const [moods, setMoods] = useState([]);

  // Fetch moods and songs from backend
  useEffect(() => {
    const fetchMoods = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/moods/");
        setMoods(response.data);
      } catch (error) {
        console.error("Error fetching moods:", error);
      }
    };
    fetchMoods();
  }, []);

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home moods={moods} />} />
        <Route path="/mood/:moodName" element={<MoodPage moods={moods} />} />
        <Route
          path="/create"
          element={<CreatePlaylist moods={moods} setMoods={setMoods} />}
        />
        <Route
          path="/view"
          element={<ViewPlaylist moods={moods} setMoods={setMoods} />}
        />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </Router>
  );
}

export default App;


