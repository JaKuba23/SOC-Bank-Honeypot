import React, { useState, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { LiveLogsTable, SuspiciousTable, TransfersTable } from '../components';
import { ThemeContext } from '../context/ThemeContext';

export default function SocDashboard() {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef(null);
  const { theme, toggleTheme } = useContext(ThemeContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await fetch("http://localhost:5000/api/logout", {
      method: "POST",
      credentials: "include",
    });
    navigate("/login");
  };

  const runTestTransfers = async () => {
    try {
      setLoading(true);
      const eventTypes = [
        "valid_transfer",
        "invalid_transfer",
        "failed_login",
        "phishing"
      ];
      const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      let body = {};
      if (eventType === "valid_transfer") {
        body = { test_type: "valid_transfer", sender: "William", recipient: "Emma", amount: 10 };
      } else if (eventType === "invalid_transfer") {
        body = { test_type: "invalid_transfer", sender: "William", recipient: "Nonexistent", amount: 999999 };
      } else if (eventType === "failed_login") {
        body = { test_type: "failed_login", username: "hacker", password: "wrongpass" };
      } else if (eventType === "phishing") {
        body = { test_type: "phishing", username: "admin", password: "wrongpass" };
      }
      const response = await fetch('http://localhost:5000/api/test-transfers', {
        method: 'POST',
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!response.ok) return;
    } catch (err) {
      // brak spamu błędów
    } finally {
      setLoading(false);
    }
  };

  const handleRunTests = () => {
    if (running) {
      clearInterval(intervalRef.current);
      setRunning(false);
    } else {
      runTestTransfers();
      intervalRef.current = setInterval(runTestTransfers, 1000);
      setRunning(true);
    }
  };

  React.useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);

  return (
    <div className="soc-dashboard-container">
      <header>
        <h1>SOC Monitoring Panel</h1>
        <div className="header-right">
          <button
            className="theme-switcher run-tests-btn"
            style={{ minWidth: 140, height: 48, fontWeight: 600 }}
            onClick={toggleTheme}
          >
            {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </button>
          <button
            className="run-tests-btn"
            onClick={handleRunTests}
            disabled={loading}
            style={{ minWidth: 140, height: 48, fontWeight: 600, opacity: loading ? 0.7 : 1 }}
          >
            {running ? 'Stop Test Events' : 'Run Test Events'}
          </button>
          <button
            className="logout-button"
            style={{ minWidth: 110, height: 48, fontWeight: 600 }}
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </header>
      <main>
        <p className="dashboard-description">
          Central monitoring station for suspicious activities and system logs.
        </p>
        {error && (
          <div className="form-error-message">
            {error}
            <button onClick={() => setError(null)} className="dismiss-button">Dismiss</button>
          </div>
        )}
        <div className="soc-grid">
          <div className="soc-panel-wide panel">
            <h2>All System Logs</h2>
            <LiveLogsTable />
          </div>
          <div className="soc-panel-half panel">
            <h2>Suspicious & Phishing Events</h2>
            <SuspiciousTable />
          </div>
          <div className="soc-panel-half panel">
            <h2>Global Live Transfers</h2>
            <TransfersTable />
          </div>
        </div>
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} Secure Bank SOC. For educational purposes only.</p>
      </footer>
    </div>
  );
}