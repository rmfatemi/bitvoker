import React, { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Container, Box, Tabs, Tab } from '@mui/material';
import { getAppTheme } from './theme';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import Settings from './components/Settings/Settings';
import Logs from './components/Logs/Logs';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [themeMode, setThemeMode] = useState(localStorage.getItem('theme') || 'dark');
    const [isLoading, setIsLoading] = useState(true);

    // State for data from API
    const [notifications, setNotifications] = useState([]);
    const [logs, setLogs] = useState([]);
    const [config, setConfig] = useState({
        show_original: true,
        gui_theme: 'dark',
        enable_ai: true,
        preprompt: "",
        telegram: {enabled: false, chat_id: '', token: ''},
        discord: {enabled: false, webhook_id: '', token: ''},
        slack: {enabled: false, webhook_id: '', token: ''},
        gotify: {enabled: false, server_url: '', token: ''}
    });

    // Apply Material UI theme
    const theme = getAppTheme(themeMode);

    // API base URL
    const API_BASE = '/api';

    useEffect(() => {
        // Load saved tab from localStorage if available
        const savedTab = localStorage.getItem('activeTab');
        if (savedTab) {
            setActiveTab(savedTab);
        }

        // Apply theme
        document.documentElement.setAttribute('data-theme', themeMode);

        // Fetch initial data
        fetchConfig();
        fetchNotifications();
        fetchLogs();
    }, [themeMode]);

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
                    setConfig({...data.config, gui_theme: themeMode});
                }
            })
            .catch(err => {
                console.error('Error fetching config:', err);
            });
    };

    const toggleTheme = () => {
        const newTheme = themeMode === 'dark' ? 'light' : 'dark';
        setThemeMode(newTheme);
        localStorage.setItem('theme', newTheme);

        // Update config with new theme
        setConfig(prevConfig => ({
            ...prevConfig,
            gui_theme: newTheme
        }));
    };

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
        localStorage.setItem('activeTab', newValue);

        // Refresh data when switching tabs
        if (newValue === 'dashboard') {
            fetchNotifications();
        } else if (newValue === 'logs') {
            fetchLogs();
        } else if (newValue === 'settings') {
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
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Box className="app-container">
                <Header toggleTheme={toggleTheme} theme={themeMode} />

                <Container maxWidth={false}>
                    <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        sx={{ mb: 2, mt: 1 }}
                    >
                        <Tab label="Dashboard" value="dashboard" />
                        <Tab label="Settings" value="settings" />
                        <Tab label="Logs" value="logs" />
                    </Tabs>

                    <Box
                        sx={{
                            border: '1px solid',
                            borderColor: 'divider',
                            p: 3,
                            minHeight: '75vh',
                            ...(activeTab === 'dashboard' || activeTab === 'logs' ? {
                                maxHeight: '125vh',
                                overflowY: 'auto'
                            } : {})
                        }}
                    >
                        {isLoading && activeTab === 'dashboard' ? (
                            <Box>Loading notifications...</Box>
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
                    </Box>
                </Container>
            </Box>
        </ThemeProvider>
    );
}

export default App;
