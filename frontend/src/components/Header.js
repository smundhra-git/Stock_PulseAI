import React, { useState } from "react";
import "./Header.css";
import logo from "../assets/logo.png"; // Ensure the correct path to your logo

function Header() {
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Simulating login state

  return (
    <div className="header">
      {/* Left - Logo */}
      <div className="logo">
        <img src={logo} alt="Stock Pulse AI" />
      </div>

      {/* Center - Navigation Menu */}
      <nav className="nav-buttons">
        <NavButton title="Technical Analysis" />
        <NavButton title="Fundamentals" />
        <NavButton title="Time Series Models" />
        <NavButton title = "Sentiments"/>
        <NavButton title="News" />
        <NavButton title="Events" />
      </nav>

      {/* Right - Conditional Rendering (Search Bar OR Login Button) */}
      <div className="right-section">
        {isLoggedIn ? (
          <>
            {/* Stock Search Input */}
            <div className="search-container">
              <span className="search-icon">&#128269;</span>
              <input type="text" placeholder="Enter Stock Symbol (e.g. AAPL)" className="stock-input" />
            </div>

            {/* Three-Line Menu Icon */}
            <div className="menu-container">
              <span className="menu-icon">&#9776;</span>
              <div className="menu-dropdown">
                <a href="#">Settings</a>
                <a href="#">Help</a>
                <a href="#">Sign Out</a>
              </div>
            </div>
          </>
        ) : (
          /* Login Button */
          <button className="login-btn" onClick={() => setIsLoggedIn(true)}>Login</button>
        )}
      </div>
    </div>
  );
}

function NavButton({ title }) {
  return <button className="nav-button">{title}</button>;
}

export default Header;
