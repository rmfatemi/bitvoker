import apprise

from typing import List, Dict, Any, Optional

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


logger = setup_logger("notifier")


class Notifier:
    def __init__(self, destinations_config: Optional[List[Dict[str, Any]]] = None):
        self.destinations_config = destinations_config if destinations_config else []
        self.apprise = apprise.Apprise()
        self.destination_instances: Dict[str, apprise.Apprise] = {}
        self._setup_destinations()

    def update_destinations(self, destinations_config: Optional[List[Dict[str, Any]]] = None):
        logger.debug(
            f"updating notification destinations: {len(destinations_config) if destinations_config else 0} destinations"
        )
        self.destinations_config = destinations_config if destinations_config else []
        self._setup_destinations()

    def _setup_destinations(self):
        self.apprise.clear()
        self.destination_instances = {}

        for destination_conf in self.destinations_config:
            if not destination_conf.get("enabled", False):
                logger.debug(f"skipping disabled destination: {destination_conf.get('name', 'unnamed destination')}")
                continue

            try:
                url = destination_conf.get("url")
                if url:
                    if isinstance(url, list):
                        logger.debug(f"url is a list for {destination_conf.get('name')}, processing each url")
                        first_url = url[0] if url else None

                        for single_url in url:
                            self.apprise.add(single_url)

                        if "name" in destination_conf and first_url:
                            destination_apprise = apprise.Apprise()
                            destination_apprise.add(first_url)
                            self.destination_instances[destination_conf["name"]] = destination_apprise
                    else:
                        self.apprise.add(url)

                        if "name" in destination_conf:
                            destination_apprise = apprise.Apprise()
                            destination_apprise.add(url)
                            self.destination_instances[destination_conf["name"]] = destination_apprise

                    logger.debug(f"added notification destination: {destination_conf.get('name')}")
                else:
                    logger.warning(
                        f"missing url for destination: {destination_conf.get('name', 'unnamed destination')}"
                    )
            except Exception as e:
                logger.error(f"failed to add destination {destination_conf.get('name', 'unknown')}: {str(e)}")

    def send_message(
        self, message_body: str, title: str = "bitvoker notification", destination_names: Optional[List[str]] = None
    ) -> None:
        if not self.destinations_config:
            logger.warning("no notification destinations configured")
            return

        message_body = truncate(message_body, 4000, preserve_newlines=True, suffix="\n[truncated]")

        try:
            if destination_names:
                success_count = 0
                for name in destination_names:
                    if name not in self.destination_instances:
                        logger.warning(f"destination not found: {name}")
                        continue

                    dest = self.destination_instances[name]
                    if isinstance(dest, list):
                        logger.error(f"destination {name} is unexpectedly a list: {dest}")
                        continue
                    elif not hasattr(dest, "notify") or not callable(dest.notify):
                        logger.error(f"destination {name} has no callable notify method. type: {type(dest)}")
                        continue

                    try:
                        if dest.notify(body=message_body, title=title):
                            success_count += 1
                        else:
                            logger.warning(f"failed to send notification to destination: {name}")
                    except Exception as e:
                        logger.error(f"error calling notify on {name}: {str(e)}")

                logger.info(f"sent notifications to {success_count}/{len(destination_names)} specified destinations")
            else:
                if isinstance(self.apprise, list):
                    logger.error(f"main apprise object is unexpectedly a list: {self.apprise}")
                    return
                elif not hasattr(self.apprise, "notify") or not callable(self.apprise.notify):
                    logger.error(f"main apprise object has no callable notify method. type: {type(self.apprise)}")
                    return

                if self.apprise.notify(body=message_body, title=title):
                    logger.info(f"successfully sent notifications to {len(self.apprise.servers())} destinations")
                else:
                    logger.warning("some or all notifications failed to send")
        except Exception as e:
            logger.error(f"failed to send notifications: {str(e)}")
