import React, { useEffect, useState } from "react";

export default function SuspiciousTable() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = () => {
      fetch("http://localhost:5000/api/logs")
        .then(res => res.json())
        .then(data => setLogs(data.filter(log => log.level === "CRITICAL" || log.level === "WARNING")));
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="panel">
      <h2>Suspicious & Phishing Events</h2>
      <table>
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Level</th>
            <th>IP</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.slice().reverse().map((log, i) => (
            <tr key={i} className={`log-level-${log.level}`}>
              <td>{log.datetime}</td>
              <td>{log.level}</td>
              <td>{log.ip}</td>
              <td>{log.msg}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}