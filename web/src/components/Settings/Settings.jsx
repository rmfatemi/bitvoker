import React, {useState, useEffect, useMemo} from 'react';
import {
    Box, Typography, Button, CircularProgress,
    Snackbar, Alert, styled, Paper, Grid
} from '@mui/material';
import DefaultRule from './DefaultRule';
import AIProvider from './AIProvider';
import RuleEditor from './RuleEditor';
import DestinationEditor from './DestinationEditor';
import DownloadConfig from './DownloadConfig';

const StyledPaper = styled(Paper)(({ theme }) => ({
    padding: '20px',
    border: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.background.default,
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

    const updateConfig = (updater) => {
        setConfigData(prev => updater(prev));
    };

    const handleCloseSnackbar = () => {
        setSnackbar({...snackbar, open: false});
    };

    const {
        aiEnabled,
        includeOriginal,
        preprompt,
        aiProvider,
        ollamaUrl,
        ollamaModel
    } = useMemo(() => {
        const defaultRule = configData?.rules?.find(r => r.name === "default-rule") || {};
        return {
            aiEnabled: defaultRule.notify?.send_ai_text?.enabled || false,
            includeOriginal: defaultRule.notify?.send_og_text?.enabled || false,
            preprompt: defaultRule.preprompt || '',
            aiProvider: configData?.ai?.provider || 'meta_ai',
            ollamaUrl: configData?.ai?.ollama?.url || '',
            ollamaModel: configData?.ai?.ollama?.model || ''
        };
    }, [configData]);

    if (loading) {
        return (
            <Box sx={{display: 'flex', justifyContent: 'center', p: 4}}>
                <CircularProgress/>
            </Box>
        );
    }

    return (
        <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2} sx={{mb: 3}}>
                <Grid item xs={12} md={8} sx={{display: 'flex', flexDirection: 'column'}}>
                    <DefaultRule
                        aiEnabled={aiEnabled}
                        includeOriginal={includeOriginal}
                        preprompt={preprompt}
                        updateConfig={updateConfig}
                        sx={{flexGrow: 1}}
                    />
                </Grid>
                <Grid item xs={12} md={4} sx={{display: 'flex', flexDirection: 'column'}}>
                    <AIProvider
                        aiProvider={aiProvider}
                        ollamaUrl={ollamaUrl}
                        ollamaModel={ollamaModel}
                        updateConfig={updateConfig}
                        sx={{flexGrow: 1}}
                    />
                </Grid>
            </Grid>

            <StyledPaper>
                <Typography variant="h6" component="h2" sx={{mb: 2}}>
                    Notification Destinations
                </Typography>
                <DestinationEditor
                    destinations={configData?.destinations || []}
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
