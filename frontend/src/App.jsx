import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';       // Upewnij się, że ścieżka jest poprawna
import Dashboard from './components/Dashboard'; // Upewnij się, że ścieżka jest poprawna

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        {/* Domyślne przekierowanie na /dashboard, jeśli użytkownik jest zalogowany,
            lub na /login, jeśli nie jest. Logika ta jest w Dashboard.jsx */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;