import React, { useState, useEffect } from "react";

export default function FriendsList({ onSelect }) {
  const [friends, setFriends] = useState([]);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("friends") || "[]");
    setFriends(saved);
  }, []);

  function addFriend(e) {
    e.preventDefault();
    const name = e.target.friendName.value.trim();
    const account = e.target.friendAccount.value.trim();
    if (!name || !account) return;
    const updated = [...friends, { name, account }];
    setFriends(updated);
    localStorage.setItem("friends", JSON.stringify(updated));
    e.target.reset();
  }

  function removeFriend(account) {
    const updated = friends.filter(f => f.account !== account);
    setFriends(updated);
    localStorage.setItem("friends", JSON.stringify(updated));
  }

  return (
    <section className="panel">
      <h2>Saved Recipients</h2>
      <form onSubmit={addFriend} style={{ marginBottom: 10 }}>
        <input name="friendName" placeholder="Name" required />
        <input name="friendAccount" placeholder="Account Number" required />
        <button type="submit">Add Friend</button>
      </form>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {friends.map(f => (
          <li key={f.account} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "4px 0" }}>
            <span>{f.name} ({f.account})</span>
            <span>
              <button onClick={() => onSelect(f.account)}>Send</button>
              <button onClick={() => removeFriend(f.account)} style={{ marginLeft: 8 }}>Remove</button>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}