import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./Header.css";
import { Search, HelpCircle, Settings, User } from "lucide-react";

function Header({ onLogout, searchInputRef }) {
  const [searchTicker, setSearchTicker] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTicker.trim()) {
      navigate(`/stock/${searchTicker.toUpperCase()}`);
      setSearchTicker("");
    }
  };

  return (
    <div className="header-wrapper">
      <div className="header">
        <div className="logo-section">
          <img src="/logo_withbg.png" alt="StockPulse Logo" className="header-logo" />
        </div>

        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-wrapper">
              <Search size={22} className="search-icon" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search ticker (e.g., AAPL)"
                value={searchTicker}
                onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
                className="search-input"
              />
            </div>
          </form>
        </div>

        <div className="actions-section">
          <button className="action-button" title="FAQ">
            <HelpCircle size={26} />
          </button>
          <button className="action-button" title="Settings">
            <Settings size={26} />
          </button>
          <div className="user-profile" onClick={() => navigate('/profile')}>
            <div className="avatar">
              <User size={24} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Header;
