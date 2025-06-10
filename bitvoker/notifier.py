import apprise

from typing import List, Dict, Any, Optional

from bitvoker.logger import setup_logger


logger = setup_logger(__name__)


class Notifier:
    def __init__(self, destinations_config: Optional[List[Dict[str, Any]]] = None):
        self.destinations_config = destinations_config if destinations_config else []
        self.apprise = apprise.Apprise()
        self._setup_destinations()

    def update_destinations(self, destinations_config: Optional[List[Dict[str, Any]]] = None):
        self.destinations_config = destinations_config if destinations_config else []
        self._setup_destinations()

    def _setup_destinations(self):
        self.apprise = apprise.Apprise()
        for destination_conf in self.destinations_config:
            if not destination_conf.get("enabled", False):
                logger.debug(f"skipping disabled destination: {destination_conf.get('name', 'unnamed destination')}")
                continue
            try:
                url = destination_conf.get("url")
                name = destination_conf.get("name")
                if url and name:
                    self.apprise.add(url, tag=name)
                    logger.debug(f"added notification destination: {name}")
            except Exception as e:
                logger.error(f"failed to add destination {destination_conf.get('name', 'unknown')}: {str(e)}")

    def send_message(
        self, message_body: str, title: str = "bitvoker notification", destination_names: Optional[List[str]] = None
    ) -> None:
        if not self.apprise.servers:
            logger.warning("no notification destinations configured or loaded")
            return

        try:
            tags_to_notify = set(destination_names) if destination_names else None
            if not tags_to_notify:
                target_servers = self.apprise.servers
            else:
                target_servers = [s for s in self.apprise.servers if tags_to_notify.intersection(s.tags)]

            if not target_servers:
                logger.warning(f"no notification services found for specified tags: {destination_names}")
                return

            success_count = 0
            for server in target_servers:
                try:
                    temp_notifier = apprise.Apprise()
                    temp_notifier.add(server.url(privacy=False))

                    max_len = getattr(server, "body_maxlen", 0)
                    if not max_len or len(message_body) <= max_len:
                        if temp_notifier.notify(body=message_body, title=title):
                            success_count += 1
                        continue

                    SAFETY_BUFFER = 50
                    title_header_template = f"{title} (99/99)"
                    content_per_chunk = max_len - len(title_header_template) - SAFETY_BUFFER
                    if content_per_chunk <= 0:
                        logger.error(f"cannot split message for {server.service_name}; limit is too small")
                        continue

                    chunks = [
                        message_body[i : i + content_per_chunk] for i in range(0, len(message_body), content_per_chunk)
                    ]
                    total_chunks = len(chunks)

                    chunk_success = True
                    for i, chunk in enumerate(chunks):
                        part_number = i + 1
                        paginated_title = f"{title} ({part_number}/{total_chunks})"
                        if not temp_notifier.notify(body=chunk, title=paginated_title):
                            chunk_success = False

                    if chunk_success:
                        success_count += 1

                except Exception as e:
                    logger.error(f"failed to send to destination {server.service_name}: {e}", exc_info=True)

            logger.info(f"successfully sent notifications to {success_count}/{len(target_servers)} destinations")

        except Exception as e:
            logger.error(
                f"an unexpected error occurred sending notifications for tag(s) '{destination_names}': {str(e)}",
                exc_info=True,
            )
