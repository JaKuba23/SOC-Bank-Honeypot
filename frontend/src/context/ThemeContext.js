import React, { createContext, useState, useEffect, useMemo } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const localTheme = localStorage.getItem('appTheme');
    return localTheme || 'light'; // Domyślnie jasny motyw
  });

  useEffect(() => {
    localStorage.setItem('appTheme', theme);
    document.documentElement.setAttribute('data-theme', theme); // Ustaw atrybut na <html>
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  // Użyj useMemo, aby uniknąć niepotrzebnych re-renderów konsumentów kontekstu
  const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};