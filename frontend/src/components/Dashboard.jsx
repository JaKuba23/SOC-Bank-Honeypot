import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { TransferForm, HistoryTable, Loading, Error } from "./index";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loggedOut, setLoggedOut] = useState(false);
  const [error, setError] = useState("");
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      try {
        const res = await fetch("http://localhost:5000/api/me", { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
          // Filtrowanie historii tylko do transakcji powiązanych z kontem użytkownika
          const userAccount = data.account;
          const filteredHistory = (data.history || []).filter(
            h =>
              h.sender_account === userAccount ||
              h.recipient_account === userAccount ||
              h.sender === data.fullname ||
              h.recipient === data.fullname ||
              h.sender_name === data.fullname ||
              h.recipient_name === data.fullname
          );
          setHistory(filteredHistory);
        } else {
          setLoggedOut(true);
        }
      } catch (err) {
        setError("Failed to load user data.");
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [refreshTrigger]);

  const handleLogout = async () => {
    await fetch("http://localhost:5000/api/logout", {
      method: "POST",
      credentials: "include",
    });
    setLoggedOut(true);
  };

  const handleTransferSuccess = () => {
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
        <HistoryTable history={history} />
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} Secure Bank. For educational purposes only.</p>
      </footer>
      {error && <Error message={error} />}
    </div>
  );
}