import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Loading from './Loading'; // Załóżmy, że masz komponent Loading

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = loading, true = auth, false = not auth
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      try {
        // Użyj rzeczywistego endpointu /api/me do weryfikacji
        const response = await fetch('http://localhost:5000/api/me', { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          if (data.logged_in) {
            setIsAuthenticated(true);
            setIsAdmin(data.role === 'admin');
          } else {
            setIsAuthenticated(false);
          }
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error("Auth verification failed:", error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    verifyAuth();
  }, []);

  if (loading) {
    return <Loading message="Verifying authentication..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin) {
    // Jeśli ścieżka jest tylko dla admina, a użytkownik nim nie jest
    return <Navigate to="/dashboard" replace />; // Przekieruj na zwykły dashboard
  }

  return children;
};

export default ProtectedRoute;