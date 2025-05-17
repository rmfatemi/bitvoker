import requests

from bitvoker.utils import setup_logger, truncate

logger = setup_logger("notifier")


class Notifier:
    def __init__(self, channels_config):
        self.channels_config = channels_config if channels_config else []

    def _send_telegram(self, config, message, title):
        full_message = f"{title}\n\n{message}"
        full_message = truncate(full_message, 4096, preserve_newlines=True, suffix="\n[TRUNCATED]")
        payload = {"chat_id": config["chat_id"], "text": full_message}
        api_url = f"https://api.telegram.org/bot{config['token']}/sendMessage"
        try:
            response = requests.post(api_url, data=payload, timeout=10)
            response.raise_for_status()
            if not response.json().get("ok"):
                logger.error(
                    "Telegram API error for %s: %s", config.get("name", "Telegram"), response.json().get("description")
                )
                return
            logger.info("Successfully sent Telegram message for %s", config.get("name", "Telegram"))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Telegram message for %s: %s", config.get("name", "Telegram"), e)
        except Exception as ex:
            logger.error("Non-request error sending Telegram message for %s: %s", config.get("name", "Telegram"), ex)

    def _send_slack(self, config, message, title):
        full_message = f"*{title}*\n\n{message}"
        full_message = truncate(full_message, 4000, preserve_newlines=True, suffix="\n[TRUNCATED]")
        payload = {"text": full_message}
        try:
            response = requests.post(config["webhook_id"], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Slack message for %s", config.get("name", "Slack"))
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to send Slack message for %s: %s (Ensure webhook URL is correct and active)",
                config.get("name", "Slack"),
                e,
            )

    def _send_discord(self, config, message, title):
        full_message = f"**{title}**\n\n{message}"
        full_message = truncate(full_message, 2000, preserve_newlines=True, suffix="\n[TRUNCATED]")
        payload = {"content": full_message}
        try:
            response = requests.post(config["webhook_id"], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Discord message for %s", config.get("name", "Discord"))
        except requests.exceptions.RequestException as e:
            logger.error(
                "Failed to send Discord message for %s: %s (Ensure webhook URL is correct and active)",
                config.get("name", "Discord"),
                e,
            )

    def _send_gotify(self, config, message, title):
        message = truncate(message, 32768, preserve_newlines=True, suffix="\n[TRUNCATED]")
        target_url = f"{config['server_url'].rstrip('/')}/message?token={config['token']}"
        payload = {"title": title, "message": message, "priority": config.get("priority", 5)}
        try:
            response = requests.post(target_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Successfully sent Gotify message for %s", config.get("name", "Gotify"))
        except requests.exceptions.RequestException as e:
            logger.error("Failed to send Gotify message for %s: %s", config.get("name", "Gotify"), e)

    def send_message(self, message_body, title="Bitvoker Notification"):
        if not self.channels_config:
            logger.warning("No notification channels configured.")
            return
        for channel_conf_wrapper in self.channels_config:
            if not channel_conf_wrapper.get("enabled", False):
                logger.debug("Skipping disabled channel: %s", channel_conf_wrapper.get("name", "Unnamed Channel"))
                continue
            channel_type = channel_conf_wrapper.get("type")
            specific_config = channel_conf_wrapper.get("config", {})
            specific_config["name"] = channel_conf_wrapper.get("name", f"Unnamed {channel_type}")
            if not specific_config:
                logger.warning("Channel %s is enabled but has no specific config.", channel_conf_wrapper.get("name"))
                continue
            try:
                if channel_type == "telegram":
                    if "token" in specific_config and "chat_id" in specific_config:
                        self._send_telegram(specific_config, message_body, title)
                    else:
                        logger.error("Telegram channel %s missing token or chat_id.", specific_config["name"])
                elif channel_type == "slack":
                    if "webhook_id" in specific_config:
                        self._send_slack(specific_config, message_body, title)
                    else:
                        logger.error("Slack channel %s missing webhook_id.", specific_config["name"])
                elif channel_type == "discord":
                    if "webhook_id" in specific_config:
                        self._send_discord(specific_config, message_body, title)
                    else:
                        logger.error("Discord channel %s missing webhook_id.", specific_config["name"])
                elif channel_type == "gotify":
                    if "server_url" in specific_config and "token" in specific_config:
                        self._send_gotify(specific_config, message_body, title)
                    else:
                        logger.error("Gotify channel %s missing server_url or token.", specific_config["name"])
                else:
                    logger.warning(
                        "Unsupported notification channel type: %s for %s", channel_type, specific_config["name"]
                    )
            except Exception as e:
                logger.error("Unhandled error processing channel %s (%s): %s", specific_config["name"], channel_type, e)
