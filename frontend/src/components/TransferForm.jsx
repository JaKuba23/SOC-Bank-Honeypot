import React, { useState, useEffect } from "react";

export default function TransferForm({ onTransfer, selectedAccount }) {
  const [users, setUsers] = useState([]);
  const [recipient, setRecipient] = useState(selectedAccount || "");
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/api/users", { credentials: "include" })
      .then(res => res.json())
      .then(setUsers);
  }, []);

  useEffect(() => {
    if (selectedAccount) setRecipient(selectedAccount);
  }, [selectedAccount]);

  async function handleSubmit(e) {
    e.preventDefault();
    setResult("");
    setError("");
    if (!recipient || !amount) {
      setError("Recipient account and amount are required");
      return;
    }
    const res = await fetch("http://localhost:5000/api/transfer", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipient_account: recipient, amount_eur: amount }),
    });
    const data = await res.json();
    if (res.ok && data.new_balance !== undefined) {
      setResult(`Transfer successful! New balance: ${data.new_balance.toFixed(2)} EUR`);
      setAmount("");
      if (onTransfer) onTransfer();
    } else {
      setError(data.error || "Transfer failed");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Recipient:
        <select value={recipient} onChange={e => setRecipient(e.target.value)} required>
          <option value="">-- Select --</option>
          {users.map(u => (
            <option key={u.account} value={u.account}>
              {u.fullname} ({u.account})
            </option>
          ))}
        </select>
      </label>
      <label>
        Amount [EUR]:
        <input
          type="number"
          min="1"
          step="0.01"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          required
        />
      </label>
      <button type="submit">Transfer</button>
      {result && <div style={{ color: "green", marginTop: 8 }}>{result}</div>}
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
    </form>
  );
}