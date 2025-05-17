import requests

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


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
                    "telegram API error for %s: %s", config.get("name", "telegram"), response.json().get("description")
                )
                return
            logger.info("successfully sent telegram message for %s", config.get("name", "telegram"))
        except requests.exceptions.RequestException as e:
            logger.error("failed to send telegram message for %s: %s", config.get("name", "telegram"), e)
        except Exception as ex:
            logger.error("non-request error sending telegram message for %s: %s", config.get("name", "telegram"), ex)

    def _send_slack(self, config, message, title):
        full_message = f"*{title}*\n\n{message}"
        full_message = truncate(full_message, 4000, preserve_newlines=True, suffix="\n[TRUNCATED]")
        payload = {"text": full_message}
        try:
            response = requests.post(config["webhook_id"], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("successfully sent slack message for %s", config.get("name", "slack"))
        except requests.exceptions.RequestException as e:
            logger.error(
                "failed to send slack message for %s: %s (make sure webhook url is correct and active)",
                config.get("name", "slack"),
                e,
            )

    def _send_discord(self, config, message, title):
        full_message = f"**{title}**\n\n{message}"
        full_message = truncate(full_message, 2000, preserve_newlines=True, suffix="\n[TRUNCATED]")
        payload = {"content": full_message}
        try:
            response = requests.post(config["webhook_id"], json=payload, timeout=10)
            response.raise_for_status()
            logger.info("successfully sent discord message for %s", config.get("name", "discord"))
        except requests.exceptions.RequestException as e:
            logger.error(
                "failed to send discord message for %s: %s (make sure webhook url is correct and active)",
                config.get("name", "discord"),
                e,
            )

    def _send_gotify(self, config, message, title):
        message = truncate(message, 32768, preserve_newlines=True, suffix="\n[TRUNCATED]")
        target_url = f"{config['server_url'].rstrip('/')}/message?token={config['token']}"
        payload = {"title": title, "message": message, "priority": config.get("priority", 5)}
        try:
            response = requests.post(target_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("successfully sent gotify message for %s", config.get("name", "gotify"))
        except requests.exceptions.RequestException as e:
            logger.error("failed to send gotify message for %s: %s", config.get("name", "gotify"), e)

    def send_message(self, message_body, title="bitvoker notification"):
        if not self.channels_config:
            logger.warning("No notification channels configured.")
            return
        for channel_conf_wrapper in self.channels_config:
            if not channel_conf_wrapper.get("enabled", False):
                logger.debug("Skipping disabled channel: %s", channel_conf_wrapper.get("name", "unnamed channel"))
                continue
            channel_type = channel_conf_wrapper.get("type")
            specific_config = channel_conf_wrapper.get("config", {})
            specific_config["name"] = channel_conf_wrapper.get("name", f"unnamed {channel_type}")
            if not specific_config:
                logger.warning("channel %s is enabled but has no specific config.", channel_conf_wrapper.get("name"))
                continue
            try:
                if channel_type == "telegram":
                    if "token" in specific_config and "chat_id" in specific_config:
                        self._send_telegram(specific_config, message_body, title)
                    else:
                        logger.error("telegram channel %s missing token or chat_id.", specific_config["name"])
                elif channel_type == "slack":
                    if "webhook_id" in specific_config:
                        self._send_slack(specific_config, message_body, title)
                    else:
                        logger.error("slack channel %s missing webhook_id.", specific_config["name"])
                elif channel_type == "discord":
                    if "webhook_id" in specific_config:
                        self._send_discord(specific_config, message_body, title)
                    else:
                        logger.error("discord channel %s missing webhook_id.", specific_config["name"])
                elif channel_type == "gotify":
                    if "server_url" in specific_config and "token" in specific_config:
                        self._send_gotify(specific_config, message_body, title)
                    else:
                        logger.error("gotify channel %s missing server_url or token.", specific_config["name"])
                else:
                    logger.warning(
                        "unsupported notification channel type: %s for %s", channel_type, specific_config["name"]
                    )
            except Exception as e:
                logger.error("unhandled error processing channel %s (%s): %s", specific_config["name"], channel_type, e)
