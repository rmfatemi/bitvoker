import React from 'react';
import bitvokerLogo from '../../assets/bitvoker.png';

function Header({toggleTheme, theme}) {
    return (
        <header>
            <div className="logo-container">
                <img
                    src={bitvokerLogo}
                    alt="Bitvoker Logo"
                    className="app-logo"
                    width="32"
                    height="32"
                    style={{marginRight: '5px'}}
                />
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
