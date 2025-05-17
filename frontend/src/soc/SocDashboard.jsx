import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LiveLogsTable, SuspiciousTable, TransfersTable } from '../components';
import ThemeSwitcher from '../components/ThemeSwitcher';

export default function SocDashboard() {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef(null);
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
        // ...twój kod losowania eventu...
        const response = await fetch('http://localhost:5000/api/test-transfers', {
        method: 'POST',
        credentials: 'include',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
        });
        
        if (!response.ok) return;
    
    } catch (err) {
     
    } finally {
        setLoading(false);
    }
    };

    // Start/stop loop
    const handleToggle = () => {
        if (running) {
        clearInterval(intervalRef.current);
        setRunning(false);
        } else {
        runTestTransfers(); // natychmiast po kliknięciu
        intervalRef.current = setInterval(runTestTransfers, 1000);
        setRunning(true);
        }
    };

  // Sprzątanie po odmontowaniu
  React.useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);

  return (
    <div className="soc-dashboard-container">
      <header>
        <div className="header-left">
          <h1>SOC Monitoring Panel</h1>
        </div>
        <div className="header-right">
          <ThemeSwitcher />
          <button
            className={`test-transfers-btn ${loading ? 'disabled' : ''}`}
            onClick={handleToggle}
            disabled={loading}
          >
            {running ? 'Stop Test Events' : 'Run Test Events'}
          </button>
          <button className="logout-button" onClick={handleLogout}>Logout</button>
          <Link to="/dashboard" className="back-to-dashboard-link">User Dashboard</Link>
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