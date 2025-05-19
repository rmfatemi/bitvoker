import React, {useState, useEffect} from 'react';
import ChannelCard from './ChannelCard';
import telegramLogo from '../../assets/telegram.svg';
import discordLogo from '../../assets/discord.svg';
import slackLogo from '../../assets/slack.svg';
import gotifyLogo from '../../assets/gotify.svg';

function Settings({config = {}, onSave}) {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);

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
                        url: 'http://<server-ip>:11434',
                        model: 'gemma3:1b'
                    },
                    telegram: data.telegram || {enabled: false, chat_id: '', token: ''},
                    discord: data.discord || {enabled: false, webhook_id: '', token: ''},
                    slack: data.slack || {enabled: false, webhook_id: '', token: ''},
                    gotify: data.gotify || {enabled: false, server_url: '', token: ''}
                });
            } catch (error) {
                console.error('Failed to fetch config:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchConfig();
    }, []);

    const updateConfig = (channel, key, value) => {
        setSettings({
            ...settings,
            [channel]: {
                ...settings[channel],
                [key]: value
            }
        });
    };

    if (loading) {
        return <div>Loading...</div>;
    }

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

    const channelConfigs = {
        telegram: {
            icon: <img src={telegramLogo} alt="Telegram Logo" width="20" height="20" style={{marginRight: "8px"}} />,
            title: "Telegram",
            fields: [
                {
                    id: "telegram_chat_id",
                    label: "Chat ID",
                    key: "chat_id",
                    type: "text",
                    placeholder: "Telegram Chat ID"
                },
                {
                    id: "telegram_token",
                    label: "Token",
                    key: "token",
                    type: "password",
                    placeholder: "Telegram Bot Token",
                    autoComplete: "off"
                }
            ]
        },
        discord: {
            icon: <img src={discordLogo} alt="Discord Logo" width="20" height="20" style={{marginRight: "8px"}} />,
            title: "Discord",
            fields: [
                {
                    id: "discord_webhook_id",
                    label: "Webhook ID",
                    key: "webhook_id",
                    type: "password",
                    placeholder: "Discord Webhook ID",
                    autoComplete: "off"
                },
                {
                    id: "discord_token",
                    label: "Token",
                    key: "token",
                    type: "password",
                    placeholder: "Discord Token",
                    autoComplete: "off"
                }
            ]
        },
        slack: {
            icon: <img src={slackLogo} alt="Slack Logo" width="20" height="20" style={{marginRight: "8px"}} />,
            title: "Slack",
            fields: [
                {
                    id: "slack_webhook_id",
                    label: "Webhook ID",
                    key: "webhook_id",
                    type: "password",
                    placeholder: "Slack Webhook ID",
                    autoComplete: "off"
                },
                {
                    id: "slack_token",
                    label: "Token",
                    key: "token",
                    type: "password",
                    placeholder: "Slack Token",
                    autoComplete: "off"
                }
            ]
        },
        gotify: {
            icon: <img src={gotifyLogo} alt="Gotify Logo" width="20" height="20" style={{marginRight: "8px"}} />,
            title: "Gotify",
            fields: [
                {
                    id: "gotify_server_url",
                    label: "Server URL:",
                    key: "server_url",
                    type: "text",
                    placeholder: "https://your.gotify.server"
                },
                {
                    id: "gotify_token",
                    label: "Token",
                    key: "token",
                    type: "password",
                    placeholder: "Gotify App Token",
                    autoComplete: "off"
                }
            ]
        }
    };

    return (
        <form id="settingsForm" onSubmit={handleSubmit}>
            <input type="hidden" name="gui_theme" id="gui_theme_input" value={settings.gui_theme}/>

            <h3 id="settings-general">General Settings</h3>

            {/* First row with two equal columns side by side */}
            <div className="general-settings-row"
                 style={{display: "flex", flexDirection: "row", gap: "20px", marginBottom: "20px"}}>
                {/* Column 1 - Enable AI, Show Original, and AI Provider */}
                <div style={{
                    flex: "1",
                    padding: "15px",
                    border: "1px solid #333",
                    borderRadius: "5px",
                    display: "flex",
                    flexDirection: "column",
                    height: "250px" // Exact height to match
                }}>
                    <div className="form-group">
                        <div style={{display: "flex", alignItems: "center"}}>
                            <input
                                type="checkbox"
                                id="enable_ai"
                                name="enable_ai"
                                checked={settings.enable_ai}
                                onChange={toggleAI}
                                style={{marginRight: "8px"}}
                            />
                            <label htmlFor="enable_ai" className="bold-label">Enable AI Processing</label>
                        </div>
                        <small style={{display: "block", marginTop: "-2px", marginLeft: "5px"}}>
                            Generated AI summary of received messages processed via <a href="https://www.meta.ai"
                                                                                       target="_blank"
                                                                                       rel="noopener noreferrer">Meta
                            AI</a> or <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer">Ollama</a>
                        </small>
                    </div>

                    <div className="form-group" style={{marginTop: "15px"}}>
                        <div style={{display: "flex", alignItems: "center"}}>
                            <input
                                type="checkbox"
                                id="show_original"
                                name="show_original"
                                checked={settings.show_original}
                                disabled={!settings.enable_ai}
                                onChange={handleChange}
                                style={{marginRight: "8px"}}
                            />
                            <label
                                htmlFor="show_original"
                                id="show_original_label"
                                className={!settings.enable_ai ? "disabled bold-label" : "bold-label"}
                            >
                                Show Original Message
                            </label>
                        </div>
                        <small style={{display: "block", marginTop: "-2px", marginLeft: "5px"}}>
                            If AI is enabled, appends the original to the AI summary. If AI is disabled, this is forced
                            on and the original message is sent.
                        </small>
                    </div>

                    <div className="form-group" style={{marginTop: "15px"}}>
                        <label className={!settings.enable_ai ? "disabled bold-label" : "bold-label"}>
                            AI Provider
                        </label>

                        <div style={{display: "flex", marginTop: "8px"}}>
                            <label style={{
                                display: "flex",
                                alignItems: "center",
                                marginRight: "20px"
                            }}>
                                <input
                                    type="radio"
                                    id="meta_ai"
                                    name="type"
                                    value="meta_ai"
                                    checked={settings.ai_provider.type === "meta_ai"}
                                    disabled={!settings.enable_ai}
                                    onChange={handleAIProviderChange}
                                    style={{marginRight: "8px"}}
                                />
                                <span>Meta AI</span>
                            </label>

                            <label style={{
                                display: "flex",
                                alignItems: "center"
                            }}>
                                <input
                                    type="radio"
                                    id="ollama"
                                    name="type"
                                    value="ollama"
                                    checked={settings.ai_provider.type === "ollama"}
                                    disabled={!settings.enable_ai}
                                    onChange={handleAIProviderChange}
                                    style={{marginRight: "8px"}}
                                />
                                <span>Ollama</span>
                            </label>
                        </div>

                        <small style={{display: "block", marginTop: "-2px", marginLeft: "5px"}}>
                            Select which AI provider to use for message processing
                        </small>
                    </div>
                </div>

                {/* Column 2 - URL and Model inputs */}
                <div style={{
                    flex: "1",
                    padding: "15px",
                    border: "1px solid #333",
                    borderRadius: "5px",
                    display: "flex",
                    flexDirection: "column",
                    height: "250px" // Exact height to match
                }}>
                    <div className="form-group">
                        <label
                            className={!settings.enable_ai || settings.ai_provider.type !== "ollama" ? "disabled bold-label" : "bold-label"}>
                            URL
                        </label>
                        <input
                            type="text"
                            id="ai_provider_url"
                            name="url"
                            placeholder="http://<server-ip>:11434"
                            value={settings.ai_provider.url}
                            disabled={!settings.enable_ai || settings.ai_provider.type !== "ollama"}
                            onChange={handleAIProviderChange}
                            style={{width: "100%", marginTop: "8px"}}
                        />
                        <small style={{display: "block", marginTop: "-2px", marginLeft: "5px"}}>
                            URL for the AI provider's API endpoint
                        </small>
                    </div>

                    <div className="form-group" style={{marginTop: "15px"}}>
                        <label
                            className={!settings.enable_ai || settings.ai_provider.type !== "ollama" ? "disabled bold-label" : "bold-label"}>
                            Model
                        </label>
                        <input
                            type="text"
                            id="ai_provider_model"
                            name="model"
                            placeholder="gemma3:1b"
                            value={settings.ai_provider.model}
                            disabled={!settings.enable_ai || settings.ai_provider.type !== "ollama"}
                            onChange={handleAIProviderChange}
                            style={{width: "100%", marginTop: "8px"}}
                        />
                        <small style={{display: "block", marginTop: "-2px", marginLeft: "5px"}}>
                            The model to use (e.g., gemma3:1b, llama2)
                        </small>
                    </div>
                </div>
            </div>
            {/* Second row - Prompt textarea (full width) */}
            <div className="general-settings-row">
                <div className="form-group" style={{width: "100%"}}>
                    <label
                        htmlFor="preprompt"
                        id="preprompt_label"
                        className={!settings.enable_ai ? "disabled bold-label" : "bold-label"}
                    >
                        AI Preprompt
                    </label>
                    <textarea
                        id="preprompt"
                        name="preprompt"
                        rows="6"
                        placeholder="Instructions for the AI model"
                        maxLength="2048"
                        style={{width: "100%", marginTop: "-2px"}}
                        disabled={!settings.enable_ai}
                        value={settings.preprompt}
                        onChange={handleChange}
                    />
                    <small>Instructions that guide how the AI processes messages (max 2048 chars)</small>
                </div>
            </div>

            <h3 id="settings-notifications">Notification Channels</h3>

            <div className="channel-row">
                {/* Telegram and Discord channels */}
                <ChannelCard
                    channel="telegram"
                    config={settings.telegram}
                    updateConfig={updateConfig}
                    icon={channelConfigs.telegram.icon}
                    title={channelConfigs.telegram.title}
                    fields={channelConfigs.telegram.fields}
                />
                <ChannelCard
                    channel="discord"
                    config={settings.discord}
                    updateConfig={updateConfig}
                    icon={channelConfigs.discord.icon}
                    title={channelConfigs.discord.title}
                    fields={channelConfigs.discord.fields}
                />
            </div>

            <div className="channel-row">
                {/* Slack and Gotify channels */}
                <ChannelCard
                    channel="slack"
                    config={settings.slack}
                    updateConfig={updateConfig}
                    icon={channelConfigs.slack.icon}
                    title={channelConfigs.slack.title}
                    fields={channelConfigs.slack.fields}
                />
                <ChannelCard
                    channel="gotify"
                    config={settings.gotify}
                    updateConfig={updateConfig}
                    icon={channelConfigs.gotify.icon}
                    title={channelConfigs.gotify.title}
                    fields={channelConfigs.gotify.fields}
                />
            </div>

            <button type="submit" className="button" style={{marginTop: "20px"}}>Save All Settings</button>
        </form>
    );
}

export default Settings;
