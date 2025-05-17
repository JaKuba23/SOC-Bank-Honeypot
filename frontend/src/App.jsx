import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import SocDashboard from './soc/SocDashboard';
import { ThemeProvider } from './context/ThemeContext'; // Import ThemeProvider
import ProtectedRoute from './components/ProtectedRoute'; // Komponent do ochrony ścieżek

function App() {
  return (
    <ThemeProvider> {/* Owijamy całą aplikację */}
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/soc-dashboard" 
            element={
              <ProtectedRoute adminOnly={true}> {/* Tylko admin ma dostęp */}
                <SocDashboard />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/login" replace />} /> {/* Domyślnie na login */}
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;