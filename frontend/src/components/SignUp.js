import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Signup() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  const handleSignup = async (e) => {
    e.preventDefault()

    try {
      const response = await fetch('http://localhost:8000/api/signup', { // ✅ Fixed URL
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      
      const data = await response.json()

      if (response.ok) {
        setMessage('Account created! Redirecting...')
        setTimeout(() => navigate('/login'), 2000)
      } else {
        setMessage(data.detail || 'Signup failed')  // ✅ `data.detail` fixes error handling
      }
    } catch (error) {
      setMessage('Server error. Try again later.')
    }
  }

  return (
    <div>
      <h2>Sign Up</h2>
      {message && <p>{message}</p>}
      <form onSubmit={handleSignup}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Sign Up</button>
      </form>
    </div>
  )
}

export default Signup
