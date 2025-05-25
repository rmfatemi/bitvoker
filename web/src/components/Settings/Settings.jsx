import React, {useState, useEffect} from 'react';
import {
    Box, Typography, Button, CircularProgress,
    Snackbar, Alert, styled, Paper
} from '@mui/material';
import DefaultRule from './DefaultRule';
import AIProvider from './AIProvider';
import RuleEditor from './RuleEditor';
import ChannelEditor from './ChannelEditor';
import DownloadConfig from './DownloadConfig';

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
    const [snackbar, setSnackbar] = useState({open: false, message: '', severity: 'success'});

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

            await fetchConfig(); // Refetch config to ensure UI consistency if server modifies data

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

    const updateConfig = (updater) => {
        setConfigData(prev => updater(prev));
    };

    const handleCloseSnackbar = () => {
        setSnackbar({...snackbar, open: false});
    };

    if (loading) {
        return (
            <Box sx={{display: 'flex', justifyContent: 'center', p: 4}}>
                <CircularProgress/>
            </Box>
        );
    }

    // Extract values for component props
    const aiEnabled = configData?.ai?.enabled || false;
    const aiProvider = configData?.ai?.provider || 'meta_ai';
    const ollamaUrl = configData?.ai?.ollama?.url || '';
    const ollamaModel = configData?.ai?.ollama?.model || '';
    const defaultRule = configData?.rules?.find(r => r.name === "default-rule") || {};
    const preprompt = defaultRule?.preprompt || '';
    const showOriginal = defaultRule?.notify?.original_message?.enabled || false;

    return (
        <Box component="form" onSubmit={handleSubmit}>
            <Typography variant="h5" component="h1" sx={{mb: 3}}>
                Settings
            </Typography>

            {/* Flex container for DefaultRule and AIProvider */}
            <Box sx={{display: 'flex', flexDirection: 'row', gap: '20px', marginBottom: '20px'}}>
                <Box sx={{flex: '2 1 0%'}}> {/* DefaultRule takes 2/3 width */}
                    <DefaultRule
                        aiEnabled={aiEnabled}
                        showOriginal={showOriginal}
                        preprompt={preprompt}
                        updateConfig={updateConfig}
                    />
                </Box>
                <Box sx={{flex: '1 1 0%'}}> {/* AIProvider takes 1/3 width */}
                    <AIProvider
                        aiProvider={aiProvider}
                        ollamaUrl={ollamaUrl}
                        ollamaModel={ollamaModel}
                        updateConfig={updateConfig}
                    />
                </Box>
            </Box>

            <StyledPaper>
                <Typography variant="h6" component="h2" sx={{mb: 2}}>
                    Notification Channels
                </Typography>
                <ChannelEditor
                    channels={configData?.notification_channels || []}
                    updateConfig={updateConfig}
                />
            </StyledPaper>

            <StyledPaper>
                <Typography variant="h6" component="h2" sx={{mb: 2}}>
                    Rules Configuration
                </Typography>
                <RuleEditor
                    rules={configData?.rules || []}
                    updateConfig={updateConfig}
                />
            </StyledPaper>

            <Box sx={{display: 'flex', gap: 2, mt: 3}}>
                <Button
                    variant="contained"
                    type="submit"
                    size="large"
                    disabled={saving}
                >
                    {saving ? 'Saving...' : 'Save Settings'}
                </Button>
                <DownloadConfig configData={configData}/>
            </Box>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
            >
                <Alert
                    onClose={handleCloseSnackbar}
                    severity={snackbar.severity}
                    sx={{width: '100%'}}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
}

export default Settings;
