import React from "react";

export default function Error({ message }) {
  if (!message) return null;
  return (
    <div className="error-msg" style={{ marginTop: 15, padding: 10, textAlign: 'center' }}>
      {message}
    </div>
  );
}