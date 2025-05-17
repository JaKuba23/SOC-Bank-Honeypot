import React, { useState, useEffect } from "react";

export default function LiveLogsTable() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = () => {
      fetch("http://localhost:5000/api/logs")
        .then(res => res.json())
        .then(setLogs);
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="panel">
      <h2>Live SOC Logs</h2>
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
          {logs.map((log, i) => (
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