import apprise
from typing import List, Dict, Any, Optional

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


logger = setup_logger("notifier")


class Notifier:
    def __init__(self, channels_config: Optional[List[Dict[str, Any]]] = None):
        self.channels_config = channels_config if channels_config else []
        self.apprise = apprise.Apprise()
        self.channel_instances = {}
        self._setup_notification_channels()

    def update_channels(self, channels_config: Optional[List[Dict[str, Any]]] = None):
        logger.debug(f"updating notification channels: {len(channels_config) if channels_config else 0} channels")
        self.channels_config = channels_config if channels_config else []
        self._setup_notification_channels()

    def _setup_notification_channels(self):
        self.apprise.clear()
        self.channel_instances = {}

        for channel_conf in self.channels_config:
            if not channel_conf.get("enabled", False):
                logger.debug(f"skipping disabled channel: {channel_conf.get('name', 'unnamed channel')}")
                continue

            try:
                url = self._build_apprise_url(channel_conf)
                if url:
                    self.apprise.add(url)

                    if "name" in channel_conf:
                        channel_apprise = apprise.Apprise()
                        channel_apprise.add(url)
                        self.channel_instances[channel_conf["name"]] = channel_apprise

                    logger.debug(f"added notification channel: {channel_conf.get('name')}")
            except Exception as e:
                logger.error(f"failed to add channel {channel_conf.get('name', 'unknown')}: {str(e)}")

    def _build_apprise_url(self, channel_conf: Dict[str, Any]) -> Optional[str]:
        channel_type = channel_conf.get("type")
        config = channel_conf.get("config", {})

        if channel_type == "telegram" and "token" in config and "chat_id" in config:
            return f"tgram://{config['token']}/{config['chat_id']}"

        elif channel_type == "slack" and "webhook_id" in config:
            return f"slack://{config['webhook_id']}"

        elif channel_type == "discord" and "webhook_id" in config:
            return config["webhook_id"]

        elif channel_type == "gotify" and "server_url" in config and "token" in config:
            return f"gotify://{config['server_url'].rstrip('/')}/{config['token']}"

        elif channel_type == "pushover" and "user_key" in config and "token" in config:
            return f"pover://{config['user_key']}/{config['token']}"

        elif channel_type == "ntfy" and "topic" in config:
            return f"ntfy://{config['topic']}"

        elif "url" in channel_conf:
            return channel_conf["url"]

        else:
            logger.warning(f"unsupported or incomplete notification channel: {channel_conf.get('name')}")
            return None

    def send_message(
        self, message_body: str, title: str = "bitvoker notification", channel_names: List[str] = None
    ) -> None:
        if not self.channels_config:
            logger.warning("no notification channels configured")
            return

        message_body = truncate(message_body, 4000, preserve_newlines=True, suffix="\n[TRUNCATED]")

        try:
            if channel_names:
                success_count = 0
                for name in channel_names:
                    if name in self.channel_instances:
                        if self.channel_instances[name].notify(body=message_body, title=title):
                            success_count += 1
                        else:
                            logger.warning(f"failed to send notification to channel: {name}")

                logger.info(f"sent notifications to {success_count}/{len(channel_names)} specified channels")

            else:
                if self.apprise.notify(body=message_body, title=title):
                    logger.info(f"successfully sent notifications to {len(self.apprise.servers())} channels")
                else:
                    logger.warning("some or all notifications failed to send")

        except Exception as e:
            logger.error(f"failed to send notifications: {str(e)}")
