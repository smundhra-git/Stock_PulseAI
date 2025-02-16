import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css"; // Import your CSS file

function Login({ setIsAuthenticated }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSignup, setIsSignup] = useState(false); // ✅ Toggle between Login & Signup
  const navigate = useNavigate();

  // ✅ Handles Login API Request
  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("token", data.access_token);
        setIsAuthenticated(true);
        navigate("/dashboard");
      } else {
        setError(data.detail || "Invalid credentials");
      }
    } catch (error) {
      setError("Server error. Try again later.");
    }
  };

  // ✅ Handles Signup API Request
  const handleSignup = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8000/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("Account created! Redirecting...");
        setTimeout(() => {
          setIsSignup(false); // ✅ Switch back to login after signup
        }, 2000);
      } else {
        setMessage(data.detail || "Signup failed");
      }
    } catch (error) {
      setMessage("Server error. Try again later.");
    }
  };

  return (
    <div className="login-container">
      {/* Left Side - Image */}
      <div className="login-left">
        <img
          src="login.png"
          alt="Stock analysis mobile app preview"
          className="phones-image"
        />
      </div>

      {/* Right Side - Login & Signup Form */}
      <div className="login-right">
        {/* Logo & Branding */}
        <div className="logo-container">
          <svg
            className="chart-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M3 3v18h18" />
            <path d="m19 9-5 5-4-4-3 3" />
          </svg>
          <img src="logo_withbg.png" alt="StockAnal Logo" className="logo-img" />
        </div>

        {/* Toggle Between Login & Signup */}
        <h2>{isSignup ? "Sign Up" : "Login"}</h2>

        {/* Error or Success Message */}
        {error && <p className="error-message">{error}</p>}
        {message && <p className="success-message">{message}</p>}

        {/* Login Form */}
        {!isSignup ? (
          <form className="login-form" onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="text"
                placeholder="Enter your email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit">Log In</button>
          </form>
        ) : (
          // Signup Form
          <form className="login-form" onSubmit={handleSignup}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="text"
                placeholder="Enter your email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit">Sign Up</button>
          </form>
        )}

        {/* Switch Between Login & Signup */}
        <div className="switch-container">
        <p>
          {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
          <button className="switch-link" onClick={() => setIsSignup(!isSignup)}>
            {isSignup ? "Log in" : "Sign up"}
          </button>
        </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
