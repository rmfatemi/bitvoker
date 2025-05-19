from typing import Optional, Any

from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.notifier import Notifier
from bitvoker.logger import setup_logger


logger = setup_logger("components")


def refresh_components(app: Any, component_types: Optional[list] = None) -> None:
    logger.info(f"refreshing components: {component_types or 'all'}")
    config = Config()

    if component_types is None or "ai" in component_types:
        _refresh_ai_component(app, config)

    if component_types is None or "servers" in component_types:
        for server_type in ["secure_tcp_server", "plain_tcp_server"]:
            if hasattr(app.state, server_type):
                _refresh_server_components(getattr(app.state, server_type), app, config)

    if component_types is None or "servers" in component_types:
        updated_servers = {}
        for server_type in ["secure_tcp_server", "plain_tcp_server"]:
            if hasattr(app.state, server_type):
                updated_servers[server_type.split("_")[0]] = getattr(app.state, server_type)
            else:
                updated_servers[server_type.split("_")[0]] = None
        app.state.tcp_servers = updated_servers


def _refresh_ai_component(app: Any, config: Optional[Config] = None) -> None:
    if config is None:
        config = Config()

    ai_provider_config = config.get_ai_provider_config()
    preprompt = config.get_preprompt()

    if config.get_enable_ai():
        need_new_ai = (
            not hasattr(app.state, "ai")
            or app.state.ai is None
            or getattr(app.state.ai, "preprompt", None) != preprompt
            or app.state.ai.needs_update(ai_provider_config)
        )

        if need_new_ai:
            if hasattr(app.state, "ai") and app.state.ai is not None:
                logger.info("cleaning up previous ai instance")
                app.state.ai.cleanup()

            logger.info(f"creating new ai instance with provider: {ai_provider_config.get('type', 'unknown')}")
            app.state.ai = AI(preprompt, provider_config=ai_provider_config, config_manager=config)

            for server_type in ["secure_tcp_server", "plain_tcp_server"]:
                if hasattr(app.state, server_type):
                    setattr(getattr(app.state, server_type), "ai", app.state.ai)
    else:
        if hasattr(app.state, "ai") and app.state.ai is not None:
            logger.info("ai is disabled, removing dangling ai instance")
            app.state.ai.cleanup()
            app.state.ai = None


def _refresh_server_components(server: Any, app: Any, config: Optional[Config] = None) -> Any:
    if config is None:
        config = Config()

    server.config_manager = config
    server.ai = app.state.ai if hasattr(app.state, "ai") else None

    channels = config.get_notification_channels()
    if hasattr(server, "notifier") and server.notifier is not None:
        logger.debug("updating existing notifier with new channels")
        server.notifier.update_channels(channels)
    else:
        logger.info("creating new notifier")
        server.notifier = Notifier(channels)

    return server
