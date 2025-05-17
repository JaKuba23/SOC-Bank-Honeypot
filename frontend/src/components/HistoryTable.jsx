import React, { useState, useEffect } from "react";

export default function HistoryTable() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/me", { credentials: "include" })
      .then(res => res.json())
      .then(data => setHistory(data.history || []));
  }, []);

  return (
    <section className="panel">
      <h2>Transaction History</h2>
      <table>
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Type</th>
            <th>Counterparty</th>
            <th>Amount [EUR]</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          {history.map((h, i) => (
            <tr key={i}>
              <td>{h.datetime}</td>
              <td>{h.type}</td>
              <td>
                {h.type === "incoming"
                  ? `${h.sender_name} (${h.sender_account})`
                  : `${h.recipient_name} (${h.recipient_account})`}
              </td>
              <td>{h.amount_eur}</td>
              <td>{h.ip}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}