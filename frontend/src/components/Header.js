import React from "react";
import "./Header.css";
import { Search, Folder, HelpCircle, Settings, User } from "lucide-react"

function Header() {
  
  return (
    
    <div className="header">
      <div className="logo">
        <img src="logo.png" alt="StockAnal Logo" className="logo-img" />
      </div>

      <div className="search-container">
        <div className="search-wrapper">
          <Search className="search-icon" />
          <input type="search" className="search-input" placeholder="Search for a stock/ETF..." />
        </div>
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
