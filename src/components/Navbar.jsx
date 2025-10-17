import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-logo">🎧 TuneMatch</div>

      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        <li><Link to="/create">Create Playlist</Link></li>
        <li><Link to="/view">View Playlist</Link></li>
      </ul>

      <div className="nav-actions">
        <Link to="/login" className="nav-btn">Login</Link>
        <Link to="/signup" className="nav-btn">Signup</Link>
      </div>
    </nav>
  );
}

export default Navbar;
