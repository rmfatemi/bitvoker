import requests

from bitvoker.logger import setup_logger

logger = setup_logger("notifier")


class Notifier:
    def __init__(self, channels_config):
        self.channels_config = channels_config if channels_config else []

    def _send_ntfy(self, config, message, title):
        target_url = f"{config['server_url'].rstrip('/')}/{config['topic']}"
        try:
            headers = {'Title': title.encode('utf-8')}
            response = requests.post(target_url, data=message.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent ntfy notification to topic %s via %s", config['topic'],
                        config.get('name', 'Ntfy'))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send ntfy notification for %s: %s", config.get('name', 'Ntfy'), e)

    def _send_telegram(self, config, message, title):
        full_message = f"{title}\n\n{message}"
        if len(full_message) > 4096:  # Telegram message limit
            full_message = full_message[:4093] + "..."
        payload = {"chat_id": config['chat_id'], "text": full_message}
        api_url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        try:
            response = requests.post(api_url, data=payload, timeout=10)
            response.raise_for_status()
            if not response.json().get('ok'):
                logger.error("Telegram API error for %s: %s", config.get('name', 'Telegram'),
                             response.json().get('description'))
                return
            logger.info("Successfully sent Telegram message for %s", config.get('name', 'Telegram'))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Telegram message for %s: %s", config.get('name', 'Telegram'), e)
        except Exception as ex:
            logger.error("Non-request error sending Telegram message for %s: %s", config.get('name', 'Telegram'), ex)

    def _send_slack(self, config, message, title):
        full_message = f"*{title}*\n\n{message}"
        payload = {"text": full_message}
        try:
            response = requests.post(config['webhook_url'], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Slack message for %s", config.get('name', 'Slack'))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Slack message for %s: %s (Ensure webhook URL is correct and active)",
                         config.get('name', 'Slack'), e)

    def _send_discord(self, config, message, title):
        full_message = f"**{title}**\n\n{message}"
        payload = {"content": full_message}
        try:
            response = requests.post(config['webhook_url'], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Discord message for %s", config.get('name', 'Discord'))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Discord message for %s: %s (Ensure webhook URL is correct and active)",
                         config.get('name', 'Discord'), e)

    def _send_gotify(self, config, message, title):
        target_url = f"{config['server_url'].rstrip('/')}/message?token={config['app_token']}"
        payload = {"title": title, "message": message, "priority": config.get('priority', 5)}
        try:
            response = requests.post(target_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Gotify message for %s", config.get('name', 'Gotify'))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Gotify message for %s: %s", config.get('name', 'Gotify'), e)

    def send_message(self, message_body, title="Bitvoker Notification"):
        if not self.channels_config:
            logger.warning("No notification channels configured.")
            return

        for channel_conf_wrapper in self.channels_config:
            if not channel_conf_wrapper.get('enabled', False):
                logger.debug("Skipping disabled channel: %s", channel_conf_wrapper.get('name', 'Unnamed Channel'))
                continue

            channel_type = channel_conf_wrapper.get('type')
            specific_config = channel_conf_wrapper.get('config', {})

            # Add name to specific_config for logging within sender methods
            specific_config['name'] = channel_conf_wrapper.get('name', f"Unnamed {channel_type}")

            if not specific_config:
                logger.warning("Channel %s is enabled but has no specific config.", channel_conf_wrapper.get('name'))
                continue

            try:
                if channel_type == "ntfy":
                    if 'server_url' in specific_config and 'topic' in specific_config:
                        self._send_ntfy(specific_config, message_body, title)
                    else:
                        logger.error("Ntfy channel %s missing server_url or topic.", specific_config['name'])
                elif channel_type == "telegram":
                    if 'bot_token' in specific_config and 'chat_id' in specific_config:
                        self._send_telegram(specific_config, message_body, title)
                    else:
                        logger.error("Telegram channel %s missing bot_token or chat_id.", specific_config['name'])
                elif channel_type == "slack":
                    if 'webhook_url' in specific_config:
                        self._send_slack(specific_config, message_body, title)
                    else:
                        logger.error("Slack channel %s missing webhook_url.", specific_config['name'])
                elif channel_type == "discord":
                    if 'webhook_url' in specific_config:
                        self._send_discord(specific_config, message_body, title)
                    else:
                        logger.error("Discord channel %s missing webhook_url.", specific_config['name'])
                elif channel_type == "gotify":
                    if 'server_url' in specific_config and 'app_token' in specific_config:
                        self._send_gotify(specific_config, message_body, title)
                    else:
                        logger.error("Gotify channel %s missing server_url or app_token.", specific_config['name'])
                else:
                    logger.warning("Unsupported notification channel type: %s for %s", channel_type,
                                   specific_config['name'])
            except Exception as e:
                logger.error("Unhandled error processing channel %s (%s): %s", specific_config['name'], channel_type, e)
