import React, { useState, useContext } from "react";
import { ThemeContext } from "../context/ThemeContext";

export default function Login() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      let data = {};
      try {
        data = await res.json();
      } catch {
        // jeśli backend nie odpowiada JSONem
        setError("Cannot connect to server. Please try again later.");
        return;
      }
      if (res.ok && data.logged_in) {
        if (data.user && data.user.role === "admin") {
          window.location.href = "/soc-dashboard";
        } else {
          window.location.href = "/dashboard";
        }
      } else {
        setError(data.message || data.error || "Invalid username or password.");
      }
    } catch (err) {
      setError("Cannot connect to server. Please try again later.");
    }
  }

  return (
    <div className="login-page">
      <button className="theme-switcher" onClick={toggleTheme}>
        {theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
      </button>
      <div className="login-container">
        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Bank Login</h2>
          <input
            type="text"
            placeholder="Username"
            autoFocus
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
          {error && <div className="error-msg">{error}</div>}
        </form>
      </div>
    </div>
  );
}