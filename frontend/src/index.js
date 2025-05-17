import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/main.css'; // Upewnij się, że ta ścieżka jest poprawna
import App from './App';    // Upewnij się, że ta ścieżka jest poprawna

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);