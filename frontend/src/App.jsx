import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login, Dashboard } from './components';
import SocDashboard from './soc/SocDashboard';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';

const router = {
  v7_startTransition: true,
  v7_relativeSplatPath: true
};

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter future={router}>
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
              <ProtectedRoute adminOnly={true}>
                <SocDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;