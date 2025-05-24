import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Button,
    CircularProgress,
    Snackbar,
    Alert,
    styled,
    Paper
} from '@mui/material';
import DefaultRule from './DefaultRule';
import AIProvider from './AIProvider';
import RuleEditor from './RuleEditor';
import ChannelEditor from './ChannelEditor';

const StyledPaper = styled(Paper)(() => ({
    padding: '20px',
    border: '1px solid var(--border-color)',
    backgroundColor: 'var(--card-bg)',
    marginBottom: '20px'
}));

function Settings() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [configData, setConfigData] = useState(null);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

    const fetchConfig = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/config');
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }
            const data = await response.json();
            setConfigData(data);
        } catch (error) {
            console.error('Error loading config:', error);
            setSnackbar({
                open: true,
                message: `Failed to load settings: ${error.message}`,
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConfig();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData),
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            await fetchConfig();

            setSnackbar({
                open: true,
                message: 'Settings saved successfully',
                severity: 'success'
            });
        } catch (error) {
            console.error('Error saving settings:', error);
            setSnackbar({
                open: true,
                message: `Failed to save settings: ${error.message}`,
                severity: 'error'
            });
        } finally {
            setSaving(false);
        }
    };

    const updateAIEnabled = (e) => {
        const enabled = e.target.checked;
        setConfigData(prev => ({
            ...prev,
            ai: {
                ...prev.ai,
                enabled: enabled
            },
            rules: prev.rules.map(rule =>
                rule.name === "default-rule"
                    ? { ...rule, enabled: enabled }
                    : rule
            )
        }));
    };

    const updateShowOriginal = (e) => {
        const enabled = e.target.checked;
        setConfigData(prev => ({
            ...prev,
            rules: prev.rules.map(rule =>
                rule.name === "default-rule"
                    ? {
                        ...rule,
                        notify: {
                            ...rule.notify,
                            original_message: {
                                ...rule.notify.original_message,
                                enabled: enabled
                            }
                        }
                    }
                    : rule
            )
        }));
    };

    const updatePreprompt = (e) => {
        const value = e.target.value;
        setConfigData(prev => ({
            ...prev,
            rules: prev.rules.map(rule =>
                rule.name === "default-rule"
                    ? { ...rule, preprompt: value }
                    : rule
            )
        }));
    };

    const updateAIProvider = (e) => {
        const { name, value } = e.target;

        if (name === "provider") {
            setConfigData(prev => ({
                ...prev,
                ai: {
                    ...prev.ai,
                    provider: value
                }
            }));
        } else if (name === "url" || name === "model") {
            setConfigData(prev => ({
                ...prev,
                ai: {
                    ...prev.ai,
                    ollama: {
                        ...prev.ai.ollama,
                        [name]: value
                    }
                }
            }));
        }
    };

    const updateRules = (newRules) => {
        setConfigData(prev => ({
            ...prev,
            rules: newRules
        }));
    };

    const updateChannels = (newChannels) => {
        setConfigData(prev => ({
            ...prev,
            notification_channels: newChannels
        }));
    };

    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    const aiEnabled = configData?.ai?.enabled || false;
    const aiProvider = configData?.ai?.provider || 'meta_ai';
    const ollamaUrl = configData?.ai?.ollama?.url || '';
    const ollamaModel = configData?.ai?.ollama?.model || '';
    const defaultRule = configData?.rules?.find(r => r.name === "default-rule") || {};
    const preprompt = defaultRule?.preprompt || '';
    const showOriginal = defaultRule?.notify?.original_message?.enabled || false;

    return (
        <Box component="form" onSubmit={handleSubmit}>
            <Typography variant="h5" component="h1" sx={{ mb: 3 }}>
                Settings
            </Typography>

            <DefaultRule
                aiEnabled={aiEnabled}
                showOriginal={showOriginal}
                preprompt={preprompt}
                updateAIEnabled={updateAIEnabled}
                updateShowOriginal={updateShowOriginal}
                updatePreprompt={updatePreprompt}
            />

            <AIProvider
                aiProvider={aiProvider}
                ollamaUrl={ollamaUrl}
                ollamaModel={ollamaModel}
                updateAIProvider={updateAIProvider}
            />

            <StyledPaper>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                    Notification Channels
                </Typography>
                <ChannelEditor
                    channels={configData?.notification_channels || []}
                    updateChannels={updateChannels}
                />
            </StyledPaper>

            <StyledPaper>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                    Rules Configuration
                </Typography>
                <RuleEditor
                    rules={configData?.rules || []}
                    updateRules={updateRules}
                />
            </StyledPaper>

            <Button
                variant="contained"
                type="submit"
                size="large"
                sx={{ mt: 3 }}
                disabled={saving}
            >
                {saving ? 'Saving...' : 'Save Settings'}
            </Button>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={snackbar.severity}
                    sx={{ width: '100%' }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
}

export default Settings;
