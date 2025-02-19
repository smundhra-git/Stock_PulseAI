import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Front from './components/Front';
import StockAnalysis from './components/StockAnalysis';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // NULL means loading state
  const searchInputRef = useRef(null);  // Create the ref

  // Check if user is already logged in
  useEffect(() => {
    fetch('/api/check-auth', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setIsAuthenticated(data.authenticated))
      .catch(() => setIsAuthenticated(false));
  }, []);

  const handleLogout = () => {
    fetch('/api/logout', { method: 'POST', credentials: 'include' })
      .then(() => {
        setIsAuthenticated(false);
      })
      .catch(error => console.error('Logout failed:', error));
  };

  if (isAuthenticated === null) {
    return <div className="loading">Checking authentication...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Login Route - No Header */}
          <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />

          {/* Protected Routes - With Header */}
          {isAuthenticated ? (
            <>
              <Route path="/" element={
                <>
                  <Header onLogout={handleLogout} searchInputRef={searchInputRef} />
                  <div className="home-content">Welcome to StockPulse AI</div>
                </>
              } />
              
              <Route path="/stock/:ticker" element={
                <>
                  <Header onLogout={handleLogout} searchInputRef={searchInputRef} />
                  <StockAnalysis />
                </>
              } />

              <Route path="/dashboard" element={
                <div className="dashboard-container">
                  <Sidebar searchInputRef={searchInputRef} />
                  <div className="content">
                    <Header onLogout={handleLogout} searchInputRef={searchInputRef} />
                    <Front />
                  </div>
                </div>
              } />
            </>
          ) : (
            // Redirect to login if not authenticated
            <Route path="*" element={<Navigate to="/login" />} />
          )}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
