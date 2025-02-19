import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Sidebar.css';
import {
  LineChart, // For market data
  Search,
  Newspaper, // For news
  Calendar, // For events
  TrendingUp, // For watchlist
  Bell, // For alerts
  BookOpen, // For research/analysis
  ChevronRight,
  ChevronLeft
} from 'lucide-react';

function Sidebar({ searchInputRef }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isExpanded, setIsExpanded] = useState(false);

  const handleItemClick = (path) => {
    if (path === '/search') {
      // Focus the search input when search icon is clicked
      searchInputRef.current?.focus();
    } else {
      navigate(path);
    }
  };

  const menuItems = [
    {
      title: 'Market Overview',
      icon: <LineChart size={24} />,
      path: '/dashboard',
      description: 'S&P 500, Market Indices, Trends'
    },
    {
      title: 'Search',
      icon: <Search size={24} />,
      path: '/search',
      description: 'Search for a stock'
    },
    {
      title: 'Latest News',
      icon: <Newspaper size={24} />,
      path: '/news',
      description: 'Financial News & Updates'
    },
    {
      title: 'Economic Calendar',
      icon: <Calendar size={24} />,
      path: '/calendar',
      description: 'Earnings, IPOs, Economic Events'
    },
    {
      title: 'Watchlist',
      icon: <TrendingUp size={24} />,
      path: '/watchlist',
      description: 'Track Your Stocks'
    },
    {
      title: 'Research & Analysis',
      icon: <BookOpen size={24} />,
      path: '/research',
      description: 'Deep Dive & Reports'
    },
    {
      title: 'Alerts',
      icon: <Bell size={24} />,
      path: '/alerts',
      description: 'Price & News Alerts'
    }
  ];

  return (
    <div className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <button 
        className="toggle-button"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? <ChevronLeft size={24} /> : <ChevronRight size={24} />}
      </button>

      <div className="sidebar-items">
        {menuItems.map((item) => (
          <div
            key={item.path}
            className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => handleItemClick(item.path)}
          >
            <div className="sidebar-icon" data-tooltip={!isExpanded ? item.title : ''}>
              {item.icon}
            </div>
            {isExpanded && (
              <div className="sidebar-content">
                <div className="sidebar-title">{item.title}</div>
                <div className="sidebar-description">{item.description}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;

