import React, { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
  e.preventDefault();
  setError("");
  const res = await fetch("http://localhost:5000/api/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (res.ok && data.logged_in) {  // ZMIENIONO: success → logged_in
    window.location.href = "/dashboard";
  } else {
    setError(data.error || "Login failed");
  }
}

  return (
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
  );
}