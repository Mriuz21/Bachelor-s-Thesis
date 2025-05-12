import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('user', 'logged-in');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('user');
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Fake News Detector</h1>
          {isAuthenticated && 
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          }
        </header>
        <main>
          <Routes>
            <Route 
              path="/login" 
              element={isAuthenticated ? <Navigate to="/home" /> : <Login onLoginSuccess={handleLogin} />} 
            />
            <Route 
              path="/register" 
              element={isAuthenticated ? <Navigate to="/home" /> : <Register />} 
            />
            <Route 
              path="/home" 
              element={isAuthenticated ? <Home /> : <Navigate to="/login" />} 
            />
            <Route 
              path="/" 
              element={<Navigate to={isAuthenticated ? "/home" : "/login"} />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;