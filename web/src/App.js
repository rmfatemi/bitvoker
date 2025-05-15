import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import Settings from './components/Settings/Settings';
import Logs from './components/Logs/Logs';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme] = useState('dark');
  const [isLoading, setIsLoading] = useState(true);

  // State for data from API
  const [notifications, setNotifications] = useState([]);
  const [logs, setLogs] = useState([]);
  const [config, setConfig] = useState({
    show_original: true,
    gui_theme: 'dark',
    enable_ai: true,
    preprompt: "",
    telegram: { enabled: false, chat_id: '', token: '' },
    discord: { enabled: false, webhook_id: '', token: '' },
    slack: { enabled: false, webhook_id: '', token: '' },
    gotify: { enabled: false, server_url: '', token: '' }
  });

  // API base URL
  const API_BASE = 'http://localhost:8085/api';

  useEffect(() => {
    // Load saved tab from localStorage if available
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab) {
      setActiveTab(savedTab);
    }

    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.body.className = savedTheme === 'light' ? 'light-mode' : '';

    // Fetch initial data
    fetchConfig();
    fetchNotifications();
    fetchLogs();
  }, []);

  const fetchNotifications = () => {
    setIsLoading(true);
    fetch(`${API_BASE}/notifications`)
      .then(res => res.json())
      .then(data => {
        if (data && data.notifications) {
          setNotifications(data.notifications);
        }
        setIsLoading(false);
      })
      .catch(err => {
        console.error('Error fetching notifications:', err);
        setIsLoading(false);
      });
  };

  const fetchLogs = () => {
    fetch(`${API_BASE}/logs`)
      .then(res => res.json())
      .then(data => {
        if (data && data.logs) {
          setLogs(data.logs);
        }
      })
      .catch(err => {
        console.error('Error fetching logs:', err);
      });
  };

  const fetchConfig = () => {
    fetch(`${API_BASE}/config`)
      .then(res => res.json())
      .then(data => {
        if (data && data.config) {
          // Preserve current theme but update all other settings
          setConfig({...data.config, gui_theme: theme});
        }
      })
      .catch(err => {
        console.error('Error fetching config:', err);
      });
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.body.className = newTheme === 'light' ? 'light-mode' : '';

    // Update config with new theme
    setConfig(prevConfig => ({
      ...prevConfig,
      gui_theme: newTheme
    }));
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    localStorage.setItem('activeTab', tab);

    // Refresh data when switching tabs
    if (tab === 'dashboard') {
      fetchNotifications();
    } else if (tab === 'logs') {
      fetchLogs();
    } else if (tab === 'settings') {
      fetchConfig();
    }
  };

  const saveConfig = (updatedConfig) => {
    fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedConfig)
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert('Settings saved!');
          // Refresh config to get any server-side updates
          fetchConfig();
        } else {
          alert(`Failed to save settings: ${data.error || 'Unknown error'}`);
        }
      })
      .catch(err => {
        console.error('Error saving settings:', err);
        alert('Failed to save settings. The API server may be down or unreachable.');
      });
  };

  return (
    <div className="app-container">
      <Header toggleTheme={toggleTheme} theme={theme} />

      <div className="container">
        <div className="tabs">
          <button
            className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => handleTabChange('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => handleTabChange('settings')}
          >
            Settings
          </button>
          <button
            className={`tab-button ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => handleTabChange('logs')}
          >
            Logs
          </button>
        </div>

        <div style={{
          border: '1px solid #ccc',
          padding: '20px',
          minHeight: '75vh',
          maxHeight: '125vh', // Limit height to 85% of viewport
          overflowY: 'auto' // Enable internal scrolling
        }}>
          {isLoading && activeTab === 'dashboard' ? (
              <div>Loading notifications...</div>
          ) : (
              <>
                {activeTab === 'dashboard' && (
                    <Dashboard
                        notifications={notifications}
                        config={config}
                        onRefresh={fetchNotifications}
                    />
                )}

                {activeTab === 'settings' && (
                    <Settings
                        config={config}
                        onSave={saveConfig}
                    />
                )}

                {activeTab === 'logs' && (
                    <Logs
                        logs={logs}
                        onRefresh={fetchLogs}
                    />
                )}
              </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
