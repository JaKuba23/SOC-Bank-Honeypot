export default function HistoryTable({ history = [], user }) {
  return (
    <section className="panel">
      <h2>Transfer History</h2>
      <table>
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Type</th>
            <th>From</th>
            <th>To</th>
            <th>Amount [EUR]</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          {history.map((h, i) => (
            <tr key={i} className={`log-level-${h.level || "INFO"}`}>
              <td>{h.datetime}</td>
              <td>{h.type}</td>
              <td>
                {h.type === "outgoing"
                  ? user?.fullname
                  : h.sender_name || h.sender || "-"}
              </td>
              <td>
                {h.type === "incoming"
                  ? user?.fullname
                  : h.recipient_name || h.recipient || "-"}
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