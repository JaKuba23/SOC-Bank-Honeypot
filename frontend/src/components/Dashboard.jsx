import React, { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import TransferForm from './TransferForm';
import HistoryTable from './HistoryTable';
import TransfersTable from './TransfersTable';
import SuspiciousTable from './SuspiciousTable';
import LiveLogsTable from './LiveLogsTable';
import Loading from './Loading';
import Error from './Error';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedAccount, setSelectedAccount] = useState("");
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchUserData = useCallback(() => {
  setLoading(true);
  fetch("http://localhost:5000/api/me", { credentials: "include" })
    .then(res => {
      if (!res.ok) {
        if (res.status === 401) {
          setUser(null);
          throw new Error(`Not authenticated: ${res.status}`);
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      console.log("User data received:", data); // Dodaj log do konsoli
      if (data.logged_in) {
        setUser(data);
        setError("");
      } else {
        console.error("Server returned logged_in=false");
        setUser(null);
      }
    })
    .catch(err => {
      console.error("Failed to fetch user data:", err);
      setError("Failed to load user data. You might be redirected to login.");
      setUser(null);
    })
    .finally(() => setLoading(false));
}, []);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  function handleLogout() {
    fetch("http://localhost:5000/api/logout", {
      method: "POST",
      credentials: "include",
    }).then(() => {
      setUser(null);
      // Pozwól Navigate zająć się przekierowaniem
    });
  }

  const handleTransferSuccess = () => {
    fetchUserData();
    setRefreshTrigger(prev => prev + 1);
  };

  if (loading) return <Loading />;
  // Jeśli nie ma użytkownika (po załadowaniu i bez błędu krytycznego), przekieruj na login
  if (!user && !error) return <Navigate to="/login" replace />;
  // Jeśli jest błąd, ale nie ma użytkownika (np. 401), też przekieruj
  if (!user && error) return <Navigate to="/login" replace />;


  return (
    <div className="dashboard-container">
      <header>
        <h1>Secure Bank <span className="soc-badge">SOC Monitored</span></h1>
        {user && ( // Sprawdź czy user istnieje przed próbą dostępu do jego właściwości
          <div className="user-info">
            <span>Welcome, {user.fullname} ({user.account})</span>
            <span className="balance">Balance: {user.balance ? user.balance.toFixed(2) : 'N/A'} EUR</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </header>
      <main>
        <div className="dashboard-grid">
          <div className="grid-col-1">
            <TransferForm onTransfer={handleTransferSuccess} selectedAccount={selectedAccount} />
            <HistoryTable key={`history-${refreshTrigger}`} />
          </div>
          <div className="grid-col-2">
            <TransfersTable key={`transfers-${refreshTrigger}`} />
            <SuspiciousTable key={`suspicious-${refreshTrigger}`} />
            <LiveLogsTable key={`logs-${refreshTrigger}`} />
          </div>
        </div>
        {error && user && <Error message={error} />} {/* Pokaż błąd tylko jeśli użytkownik jest załadowany, ale wystąpił inny błąd */}
      </main>
    </div>
  );
}