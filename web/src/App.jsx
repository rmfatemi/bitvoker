import React, { useState, useEffect } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Container, Box, Tabs, Tab } from '@mui/material';
import { getAppTheme } from './theme';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import Settings from './components/Settings/Settings';
import Logs from './components/Logs/Logs';

function App() {
    const [activeTab, setActiveTab] = useState(localStorage.getItem('activeTab') || 'dashboard');
    const [themeMode, setThemeMode] = useState(localStorage.getItem('theme') || 'dark');

    const [notifications, setNotifications] = useState([]);
    const [logs, setLogs] = useState([]);

    const [isLoading, setIsLoading] = useState({
        notifications: false,
        logs: false
    });

    const theme = getAppTheme(themeMode);
    const API_BASE = '/api';

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', themeMode);

        if (activeTab === 'dashboard') {
            fetchNotifications();
        } else if (activeTab === 'logs') {
            fetchLogs();
        }
    }, [activeTab, themeMode]);

    const fetchNotifications = () => {
        setIsLoading(prev => ({ ...prev, notifications: true }));
        fetch(`${API_BASE}/notifications`)
            .then(res => res.json())
            .then(data => {
                if (data && data.notifications) {
                    setNotifications(data.notifications);
                }
            })
            .catch(err => {
                console.error('Error fetching notifications:', err);
            })
            .finally(() => {
                setIsLoading(prev => ({ ...prev, notifications: false }));
            });
    };

    const fetchLogs = () => {
        setIsLoading(prev => ({ ...prev, logs: true }));
        fetch(`${API_BASE}/logs`)
            .then(res => res.json())
            .then(data => {
                if (data && data.logs) {
                    setLogs(data.logs);
                }
            })
            .catch(err => {
                console.error('Error fetching logs:', err);
            })
            .finally(() => {
                setIsLoading(prev => ({ ...prev, logs: false }));
            });
    };

    const toggleTheme = () => {
        const newTheme = themeMode === 'dark' ? 'light' : 'dark';
        setThemeMode(newTheme);
        localStorage.setItem('theme', newTheme);
    };

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
        localStorage.setItem('activeTab', newValue);

        // Fetch data when switching to a tab
        if (newValue === 'dashboard') {
            fetchNotifications();
        } else if (newValue === 'logs') {
            fetchLogs();
        }
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
                        {activeTab === 'dashboard' && (
                            <Dashboard
                                notifications={notifications}
                                onRefresh={fetchNotifications}
                                isLoading={isLoading.notifications}
                            />
                        )}

                        {activeTab === 'settings' && (
                            <Settings />
                        )}

                        {activeTab === 'logs' && (
                            <Logs
                                logs={logs}
                                onRefresh={fetchLogs}
                                isLoading={isLoading.logs}
                            />
                        )}
                    </Box>
                </Container>
            </Box>
        </ThemeProvider>
    );
}

export default App;
