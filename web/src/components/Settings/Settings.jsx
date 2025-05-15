import React, { useState, useEffect } from 'react';
import ChannelCard from './ChannelCard';

function Settings({ config = {}, onSave }) {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await fetch('/api/config');
        const data = await response.json();
        setSettings({
          enable_ai: data.enable_ai || false,
          show_original: data.show_original || true,
          preprompt: data.preprompt || '',
          gui_theme: data.gui_theme || 'dark',
          telegram: data.telegram || { enabled: false, chat_id: '', token: '' },
          discord: data.discord || { enabled: false, webhook_id: '', token: '' },
          slack: data.slack || { enabled: false, webhook_id: '', token: '' },
          gotify: data.gotify || { enabled: false, server_url: '', token: '' }
        });
      } catch (error) {
        console.error('Failed to fetch config:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchConfig();
  }, []);

  const toggleAI = (e) => {
    const enabled = e.target.checked;
    setSettings((prevSettings) => ({
      ...prevSettings,
      enable_ai: enabled,
      show_original: enabled ? prevSettings.show_original : true
    }));
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  const updateConfig = (channel, key, value) => {
    setSettings({
      ...settings,
      [channel]: {
        ...settings[channel],
        [key]: value
      }
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (name.includes('_config_')) {
      // Handle nested config properties (for channels)
      const [_, channel, property] = name.split('_config_');
      setSettings({
        ...settings,
        [channel]: {
          ...settings[channel],
          [property]: value
        }
      });
    } else {
      // Handle top-level properties
      setSettings({
        ...settings,
        [name]: type === 'checkbox' ? checked : value
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(settings);
  };

  const channelConfigs = {
    telegram: {
      icon: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#0088cc" viewBox="0 0 24 24" style={{ marginRight: "8px" }}>
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.96 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>,
      title: "Telegram",
      fields: [
        { id: "telegram_chat_id", label: "Chat ID:", key: "chat_id", type: "text", placeholder: "Telegram Chat ID" },
        { id: "telegram_token", label: "Bot Token:", key: "token", type: "password", placeholder: "Telegram Bot Token", autoComplete: "off" }
      ]
    },
    discord: {
      icon: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#5865F2" viewBox="0 0 24 24" style={{ marginRight: "8px" }}>
              <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/>
            </svg>,
      title: "Discord",
      fields: [
        { id: "discord_webhook_id", label: "Webhook ID:", key: "webhook_id", type: "password", placeholder: "Discord Webhook ID", autoComplete: "off" },
        { id: "discord_token", label: "Token:", key: "token", type: "password", placeholder: "Discord Token", autoComplete: "off" }
      ]
    },
    slack: {
      icon: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#611F61" viewBox="0 0 24 24" style={{ marginRight: "8px" }}>
              <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
            </svg>,
      title: "Slack",
      fields: [
        { id: "slack_webhook_id", label: "Webhook ID:", key: "webhook_id", type: "password", placeholder: "Slack Webhook ID", autoComplete: "off" },
        { id: "slack_token", label: "Token:", key: "token", type: "password", placeholder: "Slack Token", autoComplete: "off" }
      ]
    },
    gotify: {
      icon: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#0088cc" viewBox="0 0 24 24" style={{ marginRight: "8px" }}>
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>,
      title: "Gotify",
      fields: [
        { id: "gotify_server_url", label: "Server URL:", key: "server_url", type: "text", placeholder: "https://your.gotify.server" },
        { id: "gotify_token", label: "App Token:", key: "token", type: "password", placeholder: "Gotify App Token", autoComplete: "off" }
      ]
    }
  };

  return (
    <form id="settingsForm" onSubmit={handleSubmit}>
      <input type="hidden" name="gui_theme" id="gui_theme_input" value={settings.gui_theme} />

      <h3 id="settings-general">General Settings</h3>
      <div className="general-settings-row">
        <div className="form-group">
          <input
            type="checkbox"
            id="enable_ai"
            name="enable_ai"
            checked={settings.enable_ai}
            onChange={toggleAI}
          />
          <label htmlFor="enable_ai" className="bold-label">Enable AI Processing</label>
          <small style={{ display: "block", marginTop: "3px", marginLeft: "25px" }}>
            Generated AI summary of received messages processed via <a href="https://www.meta.ai" target="_blank" rel="noopener noreferrer" className="text-white">meta.ai</a>
          </small>
        </div>
        <div className="form-group">
          <input
            type="checkbox"
            id="show_original"
            name="show_original"
            checked={settings.show_original}
            disabled={!settings.enable_ai}
            onChange={handleChange}
          />
          <label
            htmlFor="show_original"
            id="show_original_label"
            className={!settings.enable_ai ? "disabled bold-label" : "bold-label"}
          >
            Show Original Message
          </label>
          <small style={{ display: "block", marginTop: "3px", marginLeft: "25px" }}>
            If AI is enabled, appends the original to the AI summary. If AI is disabled, this is forced on and the original message is sent.
          </small>
        </div>
      </div>

      <div className="general-settings-row" style={{ marginTop: "15px" }}>
        <div className="form-group" style={{ flexBasis: "100%", minWidth: "100%" }}>
          <label
            htmlFor="preprompt"
            id="preprompt_label"
            className={!settings.enable_ai ? "disabled" : ""}
          >
            AI Preprompt
          </label>
          <textarea
            id="preprompt"
            name="preprompt"
            rows="6"
            placeholder="Instructions for the AI model"
            maxLength="2048"
            style={{ width: "100%" }}
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

      <button type="submit" className="button" style={{ marginTop: "20px" }}>Save All Settings</button>
    </form>
  );
}

export default Settings;
