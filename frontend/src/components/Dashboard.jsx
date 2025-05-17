import React, { useState, useEffect, useCallback } from "react";
import { Navigate } from "react-router-dom";
import TransferForm from "./TransferForm";
import HistoryTable from "./HistoryTable";
import Loading from "./Loading";
import Error from "./Error";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [loggedOut, setLoggedOut] = useState(false);

  const fetchUserData = useCallback(() => {
    setLoading(true);
    fetch("http://localhost:5000/api/me", { credentials: "include" })
      .then(res => res.json())
      .then(data => {
        if (data.logged_in) {
          setUser(data);
          setError("");
        } else {
          setUser(null);
        }
      })
      .catch(() => {
        setError("Failed to load user data.");
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
      setLoggedOut(true);
    });
  }

  const handleTransferSuccess = () => {
    fetchUserData();
    setRefreshTrigger(prev => prev + 1);
  };

  if (loading) return <Loading />;
  if (loggedOut || (!user && !error)) return <Navigate to="/login" replace />;
  if (user && user.role === "admin") return <Navigate to="/soc-dashboard" replace />;

  return (
    <div className="dashboard-container">
      <header>
        <h1>Secure Bank SOC Monitored</h1>
        <div className="user-info">
          <span>Welcome, {user.fullname} ({user.account})</span>
          <span className="balance">Balance: {user.balance ? user.balance.toFixed(2) : 'N/A'} EUR</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>
      <main>
        <section className="panel">
          <TransferForm onTransfer={handleTransferSuccess} selectedAccount={null} />
        </section>
        <HistoryTable key={`history-${refreshTrigger}`} />
      </main>
      {error && <Error message={error} />}
    </div>
  );
}