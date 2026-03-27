import React, { useState, useEffect, useCallback } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Container, Box, Tabs, Tab } from '@mui/material';
import { getAppTheme } from './theme';
import Header from './components/Header/Header';
import Dashboard from './components/Dashboard/Dashboard';
import Settings from './components/Settings/Settings';
import Logs from './components/Logs/Logs';
import Login from './components/Login/Login';

function App() {
    const [activeTab, setActiveTab] = useState(localStorage.getItem('activeTab') || 'dashboard');
    const [themeMode, setThemeMode] = useState(localStorage.getItem('theme') || 'dark');
    const [authRequired, setAuthRequired] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token') || '');

    const [notifications, setNotifications] = useState([]);
    const [logs, setLogs] = useState([]);

    const [isLoading, setIsLoading] = useState({
        notifications: false,
        logs: false
    });

    const theme = getAppTheme(themeMode);
    const API_BASE = '/api';

    const authHeaders = useCallback(() => {
        if (!token) return {};
        return { 'Authorization': `Bearer ${token}` };
    }, [token]);

    useEffect(() => {
        fetch(`${API_BASE}/auth/status`)
            .then(res => res.json())
            .then(data => setAuthRequired(data.enabled))
            .catch(() => setAuthRequired(false));
    }, []);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', themeMode);

        if (authRequired && !token) return;

        if (activeTab === 'dashboard') {
            fetchNotifications();
        } else if (activeTab === 'logs') {
            fetchLogs();
        }
    }, [activeTab, themeMode, token, authRequired]);

    const handleAuthError = (res) => {
        if (res.status === 401) {
            setToken('');
            localStorage.removeItem('token');
        }
        return res;
    };

    const fetchNotifications = () => {
        setIsLoading(prev => ({ ...prev, notifications: true }));
        fetch(`${API_BASE}/notifications`, { headers: authHeaders() })
            .then(handleAuthError)
            .then(res => res.json())
            .then(data => {
                if (data && data.notifications) {
                    setNotifications(data.notifications);
                }
            })
            .catch(err => {
                console.error('error fetching notifications:', err);
            })
            .finally(() => {
                setIsLoading(prev => ({ ...prev, notifications: false }));
            });
    };

    const fetchLogs = () => {
        setIsLoading(prev => ({ ...prev, logs: true }));
        fetch(`${API_BASE}/logs`, { headers: authHeaders() })
            .then(handleAuthError)
            .then(res => res.json())
            .then(data => {
                if (data && data.logs) {
                    setLogs(data.logs);
                }
            })
            .catch(err => {
                console.error('error fetching logs:', err);
            })
            .finally(() => {
                setIsLoading(prev => ({ ...prev, logs: false }));
            });
    };

    const handleLogin = (newToken) => {
        setToken(newToken);
        localStorage.setItem('token', newToken);
    };

    const handleLogout = () => {
        setToken('');
        localStorage.removeItem('token');
    };

    const toggleTheme = () => {
        const newTheme = themeMode === 'dark' ? 'light' : 'dark';
        setThemeMode(newTheme);
        localStorage.setItem('theme', newTheme);
    };

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
        localStorage.setItem('activeTab', newValue);

        if (newValue === 'dashboard') {
            fetchNotifications();
        } else if (newValue === 'logs') {
            fetchLogs();
        }
    };

    if (authRequired === null) return null;

    if (authRequired && !token) {
        return (
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Login onLogin={handleLogin} />
            </ThemeProvider>
        );
    }

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Box className="app-container">
                <Header
                    toggleTheme={toggleTheme}
                    theme={themeMode}
                    onLogout={authRequired ? handleLogout : null}
                />

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
                            <Settings token={token} />
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
