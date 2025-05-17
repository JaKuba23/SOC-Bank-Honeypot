import React, { useEffect, useState } from "react";

export default function TransfersTable() {
  const [transfers, setTransfers] = useState([]);

  useEffect(() => {
    const fetchTransfers = () => {
      fetch("http://localhost:5000/api/live-transfers")
        .then(res => res.json())
        .then(setTransfers);
    };
    fetchTransfers();
    const interval = setInterval(fetchTransfers, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="panel">
      <h2>Live Transfers</h2>
      <table>
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>From</th>
            <th>To</th>
            <th>Amount [EUR]</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          {transfers.slice().reverse().map((t, i) => (
            <tr key={i}>
              <td>{t.datetime}</td>
              <td>{t.from}</td>
              <td>{t.to}</td>
              <td>{t.amount}</td>
              <td>{t.ip}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}