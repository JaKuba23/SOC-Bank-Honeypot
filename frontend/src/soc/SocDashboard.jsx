import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { LiveLogsTable, SuspiciousTable, TransfersTable } from '../components';
import ThemeSwitcher from '../components/ThemeSwitcher';

export default function SocDashboard() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Run test transfers function - for dashboard controls
  const runTestTransfers = async () => {
  try {
    setLoading(true);
    const response = await fetch('http://localhost:5000/api/test-transfers', {
      method: 'POST',
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}) // nawet jeśli nie potrzebujesz danych, wyślij pusty obiekt
    });

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Test transfers executed:', data);
  } catch (err) {
    console.error('Failed to execute test transfers:', err);
    setError('Failed to trigger test transfers. See console for details.');
  } finally {
    setLoading(false);
  }
};

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
              onClick={runTestTransfers} 
              disabled={loading}
            >
              {loading ? 'Running Tests...' : 'Run Test Transfers'}
            </button>
            <Link to="/dashboard" className="back-to-dashboard-link">User Dashboard</Link>
        </div>
      </header>
      
      <main>
        <p className="dashboard-description">Central monitoring station for suspicious activities and system logs.</p>
        
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