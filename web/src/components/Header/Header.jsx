import React from 'react';

function Header({ toggleTheme, theme }) {
  return (
    <header>
      <div className="logo-container">
        <svg id="app-logo" width="32" height="32" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <rect width="100" height="100" rx="15" fill="var(--logo-bg)"/>
          <text x="50%" y="52%" dominantBaseline="middle" textAnchor="middle" fontFamily="Arial, sans-serif" fontSize="60" fontWeight="bold" fill="var(--logo-text)">bv</text>
        </svg>
        <h1>bitvoker</h1>
      </div>
      <button
        id="themeToggle"
        className="theme-toggle-button"
        type="button"
        aria-label="Toggle theme"
        onClick={toggleTheme}
      >
        Toggle Theme
      </button>
    </header>
  );
}

export default Header;
