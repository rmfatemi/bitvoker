from typing import Optional, Any

from bitvoker.ai import AI
from bitvoker.config import Config
from bitvoker.notifier import Notifier
from bitvoker.logger import setup_logger


logger = setup_logger("components")


def refresh_server_components(server: Any, app: Optional[Any] = None, force_new_config: bool = False) -> Any:
    try:
        if force_new_config or getattr(server, "config_manager", None) is None:
            logger.info("creating new configuration manager")
            server.config_manager = Config()
        config = server.config_manager

        if config.get_enable_ai():
            ai_provider_config = config.get_ai_provider_config()
            preprompt = config.get_preprompt()

            need_new_ai = (
                server.ai is None
                or getattr(server.ai, "preprompt", None) != preprompt
                or server.ai.needs_update(ai_provider_config)
            )

            if need_new_ai:
                if hasattr(server, "ai") and server.ai is not None:
                    logger.info("cleaning up previous ai instance")
                    server.ai.cleanup()

                logger.info(f"creating new ai instance with provider: {ai_provider_config.get('type', 'unknown')}")
                server.ai = AI(preprompt, provider_config=ai_provider_config)

                if app is not None:
                    app.state.ai = server.ai
                    logger.info("ai instance attached to app state")
        else:
            logger.info("ai is disabled, removing ai instance if exists")
            if hasattr(server, "ai") and server.ai is not None:
                server.ai.cleanup()
            server.ai = None
            if app is not None and hasattr(app.state, "ai"):
                logger.info("Removing ai from app state")
                delattr(app.state, "ai")

        channels = config.get_notification_channels()
        if hasattr(server, "notifier") and server.notifier is not None:
            logger.debug("updating existing notifier with new channels")
            server.notifier.update_channels(channels)
        else:
            logger.info("creating new notifier")
            server.notifier = Notifier(channels)

        return server
    except Exception as e:
        logger.error(f"failed to refresh server components: {e}", exc_info=True)
        raise
