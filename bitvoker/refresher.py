from typing import Optional, Any

from bitvoker.config import Config
from bitvoker.notifier import Notifier
from bitvoker.alert import Alert
from bitvoker.logger import setup_logger


logger = setup_logger("components")


def refresh_components(app: Any, component_types: Optional[list] = None) -> None:
    logger.info(f"refreshing components: {component_types or 'all'}")
    config = Config()

    if component_types is None or "servers" in component_types:
        for server_type in ["secure_tcp_server", "plain_tcp_server"]:
            if hasattr(app.state, server_type):
                _refresh_server_components(getattr(app.state, server_type), app, config)

        updated_servers = {}
        for server_type in ["secure_tcp_server", "plain_tcp_server"]:
            if hasattr(app.state, server_type):
                updated_servers[server_type.split("_")[0]] = getattr(app.state, server_type)
            else:
                updated_servers[server_type.split("_")[0]] = None
        app.state.tcp_servers = updated_servers


def _refresh_server_components(server: Any, app: Any, config: Optional[Config] = None) -> Any:
    if config is None:
        config = Config()

    server.config = config

    # Update notification channels
    channels = config.get_enabled_channels()
    if hasattr(server, "notifier") and server.notifier is not None:
        logger.debug("updating existing notifier with new channels")
        server.notifier.update_channels(channels)
    else:
        logger.info("creating new notifier")
        server.notifier = Notifier(channels)

    # Create or update the alert system
    server.alert = Alert(config)

    return server
