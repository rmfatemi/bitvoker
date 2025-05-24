import React, {useState, useEffect} from 'react';
import {
    Box,
    Typography,
    Button,
    CircularProgress,
    styled,
    Paper,
    TextField
} from '@mui/material';
import ChannelEditor from './ChannelEditor';
import RuleEditor from './RuleEditor';
import AISettings from './AISettings';

// Custom styled components to match the theme system
const StyledPaper = styled(Paper)(() => ({
    padding: '15px',
    border: '1px solid var(--border-color)',
    borderRadius: '5px',
    backgroundColor: 'var(--card-bg)',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
}));

const StyledTextField = styled(TextField)(() => ({
    marginBottom: '15px',
    '& .MuiInputBase-root': {
        backgroundColor: 'var(--input-bg)',
    },
    '& .MuiOutlinedInput-root': {
        '& fieldset': {
            borderColor: 'var(--input-border)',
        },
        '&:hover fieldset': {
            borderColor: 'var(--primary-color)',
        },
    },
    '& .MuiInputLabel-root': {
        color: 'var(--text-color)',
    },
}));

function Settings({config = {}, onSave}) {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [notificationChannels, setNotificationChannels] = useState([]);

    useEffect(() => {
        async function fetchConfig() {
            try {
                const response = await fetch('/api/config');
                const data = await response.json();

                setSettings({
                    enable_ai: data.enable_ai || false,
                    show_original: data.show_original !== undefined ? data.show_original : true,
                    preprompt: data.preprompt || '',
                    gui_theme: data.gui_theme || 'dark',
                    ai_provider: data.ai_provider || {
                        type: 'ollama',
                        url: 'http://{server_ip}:11434',
                        model: 'gemma3:1b'
                    },
                    rules: data.rules || [{
                        name: "default-rule",
                        enabled: data.enable_ai || false,
                        preprompt: data.preprompt || "summarize this technical message briefly and clearly",
                        match: {
                            source: "",
                            og_text_regex: "",
                            ai_text_regex: ""
                        },
                        notify: {
                            destinations: [],
                            original_message: {
                                enabled: true,
                                match_regex: ""
                            },
                            ai_summary: {
                                enabled: true,
                                match_regex: ""
                            }
                        }
                    }]
                });

                setNotificationChannels(data.notification_channels || []);

            } catch (error) {
                console.error('Failed to fetch config:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchConfig();
    }, []);

    // Sync default rule with AI settings
    useEffect(() => {
        if (settings && settings.rules && settings.rules.length > 0) {
            // Sync the default rule with the main preprompt setting
            const updatedRules = [...settings.rules];
            updatedRules[0].preprompt = settings.preprompt;
            updatedRules[0].enabled = settings.enable_ai;

            setSettings(prev => ({
                ...prev,
                rules: updatedRules
            }));
        }
    }, [settings?.preprompt, settings?.enable_ai]);

    useEffect(() => {
        if (settings && notificationChannels && notificationChannels.length > 0) {
            const updatedSettings = {...settings};

            notificationChannels.forEach(channel => {
                if (updatedSettings[channel.name]) {
                    delete updatedSettings[channel.name];
                }
            });
            notificationChannels.forEach(channel => {
                updatedSettings[channel.name] = {
                    enabled: channel.enabled,
                    url: channel.url
                };
            });

            setSettings(updatedSettings);
        }
    }, [notificationChannels]);

    const toggleAI = (e) => {
        const enabled = e.target.checked;
        setSettings((prevSettings) => ({
            ...prevSettings,
            enable_ai: enabled,
        }));
    };

    const handleChange = (e) => {
        const {name, value, type, checked} = e.target;

        setSettings((prevSettings) => ({
            ...prevSettings,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const handleAIProviderChange = (e) => {
        const {name, value} = e.target;
        setSettings((prevSettings) => ({
            ...prevSettings,
            ai_provider: {
                ...prevSettings.ai_provider,
                [name]: value
            }
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(settings);

        setTimeout(() => {
            window.location.reload();
        }, 500);
    };

    // Function to update rules
    const updateRules = (newRules) => {
        setSettings({
            ...settings,
            rules: newRules,
            // If default rule is updated, sync its values back to the main settings
            preprompt: newRules[0]?.preprompt || settings.preprompt,
            enable_ai: newRules[0]?.enabled || settings.enable_ai
        });
    };

    if (loading) {
        return (
            <Box sx={{display: 'flex', justifyContent: 'center', p: 4}}>
                <CircularProgress/>
            </Box>
        );
    }

    return (
        <Box component="form" id="settingsForm" onSubmit={handleSubmit}>
            <input type="hidden" name="gui_theme" id="gui_theme_input" value={settings.gui_theme}/>

            <Typography variant="h5" component="h3" id="settings-general" sx={{mb: 2}}>
                General Settings
            </Typography>

            <AISettings
                settings={settings}
                toggleAI={toggleAI}
                handleChange={handleChange}
                handleAIProviderChange={handleAIProviderChange}
            />

            <Typography variant="h5" component="h3" id="settings-notifications" sx={{mb: 2}}>
                Notification Channels
            </Typography>

            <ChannelEditor
                channels={notificationChannels}
                updateChannels={setNotificationChannels}
            />

            <Typography variant="h5" component="h3" id="settings-rules" sx={{mt: 4, mb: 2}}>
                Rules Configuration
            </Typography>
            <RuleEditor
                rules={settings?.rules || []}
                updateRules={updateRules}
            />

            <Button
                variant="contained"
                type="submit"
                size="medium"
                sx={{mt: 3}}
            >
                Save Settings
            </Button>
        </Box>
    );
}

export default Settings;
