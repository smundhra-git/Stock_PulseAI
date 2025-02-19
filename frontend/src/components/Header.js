import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Header.css";
import { Search, Folder, HelpCircle, Settings, User } from "lucide-react";

function Header() {
  const [searchTicker, setSearchTicker] = useState("");
  const navigate = useNavigate();
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTicker.trim()) {
      navigate(`/stock/${searchTicker.toUpperCase()}`);
      setSearchTicker(""); // Clear the search input
    }
  };
  
  return (
    <div className="header">
      <div className="logo" onClick={() => navigate('/')}>
        <img src="/logo.png" alt="StockAnal Logo" className="logo-img" />
      </div>

      <div className="search-container">
        <form onSubmit={handleSearch} className="search-wrapper">
          <Search className="search-icon" />
          <input 
            type="search" 
            className="search-input" 
            placeholder="Enter stock ticker (e.g., AAPL)..." 
            value={searchTicker}
            onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
          />
        </form>
      </div>
      
      <div className="nav-icons">
        <Folder className="nav-icon" />
        <HelpCircle className="nav-icon" />
        <Settings className="nav-icon" />
        <div className="user-avatar">
          <User className="user-icon" />
        </div>
      </div>   
    </div>
  );
}

export default Header;
