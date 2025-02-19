import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Header from './components/Header'
import Login from './components/Login'
import Sidebar from './components/Sidebar'
import Front from './components/Front'
import StockAnalysis from './components/StockAnalysis'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
    }
  }, [])

  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/" element={<div className="home-content">Welcome to StockPulse AI</div>} />
          <Route path="/stock/:ticker" element={<StockAnalysis />} />
          <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <div className="dashboard-container">
                  <Sidebar /> {/* Sidebar now separate from main content */}
                  <div className="content">
                    <Header />
                    <Front />
                  </div>
                </div>
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
