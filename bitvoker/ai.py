import abc
import json
import requests

from meta_ai_api import MetaAI

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


logger = setup_logger("ai")


class AIProvider(abc.ABC):
    @abc.abstractmethod
    def process_message(self, prompt, max_retries=3):
        pass

    @classmethod
    @abc.abstractmethod
    def from_config(cls, config):
        pass


class MetaAIProvider(AIProvider):
    def __init__(self):
        self.bot = MetaAI()

    def process_message(self, prompt, max_retries=3):
        for retry_count in range(max_retries):
            try:
                response = self.bot.prompt(prompt)
                result = response["message"]
                logger.debug(f"meta ai processed message: {truncate(result, 80)}")
                return result
            except Exception as e:
                logger.warning(f"meta ai processing attempt {retry_count + 1} failed: {e}")
                try:
                    self.bot = MetaAI()
                except Exception as init_error:
                    logger.error(f"failed to recreate meta ai connection: {init_error}")

        logger.error("all meta ai processing attempts failed")
        raise RuntimeError(f"failed to process message after {max_retries} retries")

    @classmethod
    def from_config(cls, config):
        return cls()


class OllamaProvider(AIProvider):
    def __init__(self, url, model="gemma3:1b"):
        self.url = url
        self.model = model
        self.session = requests.Session()
        logger.info(f"initialized ollama provider with url: {url}, model: {model}")
        try:
            logger.info(f"testing connection to ollama at {self.url}...")
            health_check = self.session.get(f"{self.url}/api/tags")
            health_check.raise_for_status()
            logger.info("successfully connected to ollama service")
            self._verify_model_exists()
        except requests.exceptions.RequestException as e:
            logger.error(f"ollama service not available at {self.url}: {e}")
            logger.error("if ollama is running on a different host/container, update the url in your config")
            raise RuntimeError(f"ollama service not available: {e}")

    def _verify_model_exists(self):
        try:
            list_url = f"{self.url}/api/tags"
            response = self.session.get(list_url)
            response.raise_for_status()
            models_data = response.json()

            models = models_data.get("models", [])
            model_names = [m.get("name", "") for m in models]

            if not any(self.model == name for name in model_names):
                error_msg = f"model '{self.model}' not found in ollama. ai will be disabled."
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(f"failed to verify model exists: {e}")
            raise RuntimeError(f"failed to verify model exists: {e}")

    def process_message(self, prompt, max_retries=3):
        api_url = f"{self.url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}

        for retry_count in range(max_retries):
            try:
                response = self.session.post(api_url, json=payload)
                response.raise_for_status()
                result = response.json().get("response", "")
                logger.debug(f"ollama processed message: {truncate(result, 80)}")
                return result + "\n"
            except Exception as e:
                logger.warning(f"ollama processing attempt {retry_count + 1} failed: {e}")

        logger.error("all ollama processing attempts failed")
        raise RuntimeError(f"failed to process message after {max_retries} retries")

    @classmethod
    def from_config(cls, config):
        url = config.get("url", "http://<server-ip>:11434")
        model = config.get("model", "gemma3:1b")
        return cls(url=url, model=model)


class AI:
    def __init__(self, preprompt, provider_config=None, config_manager=None):
        self.preprompt = preprompt
        self.provider_config = provider_config or {}
        self.config_manager = config_manager
        self.provider = None
        try:
            self.provider = self._initialize_provider()
        except Exception as e:
            logger.error(f"failed to initialize ai provider: {e}")
            self.provider_config = {"type": "none", "enabled": False}
            if self.config_manager:
                logger.info("updating config manager to disable ai")
                self.config_manager.set_enable_ai(False)

    def _initialize_provider(self):
        provider_type = self.provider_config.get("type", "meta_ai")

        if provider_type == "ollama":
            logger.info("using ollama as ai provider")
            return OllamaProvider.from_config(self.provider_config)
        else:
            logger.info("using meta ai as ai provider")
            return MetaAIProvider.from_config(self.provider_config)

    def update_config(self, new_config):
        if not new_config:
            logger.warning("received empty config, ignoring update")
            return

        if self.provider_config == new_config:
            logger.debug("ai config unchanged, skipping update")
            return

        logger.info(f"updating ai config from type '{self.provider_config.get('type')}' to '{new_config.get('type')}'")
        previous_provider = self.provider
        previous_config = self.provider_config
        try:
            self.provider_config = json.loads(json.dumps(new_config))
            logger.info(f"initializing provider with type: {self.provider_config.get('type')}")
            self.provider = self._initialize_provider()
            logger.info(f"provider successfully initialized: {type(self.provider).__name__}")
            test_result = self.provider.process_message("test connection", max_retries=1)
            if test_result:
                logger.info("new provider successfully processed test message")

        except Exception as e:
            logger.error(f"failed to initialize or test provider: {str(e)}", exc_info=True)
            if previous_provider:
                logger.warning(f"reverting to previous provider: {type(previous_provider).__name__}")
                self.provider = previous_provider
                self.provider_config = previous_config
            else:
                logger.warning("ai initialization failed, disabling ai completely")
                self.provider_config = {"type": "none", "enabled": False}
                self.provider = None

    def process_message(self, message, max_retries=3):
        if not self.provider:
            logger.warning("no ai provider available, skipping message processing")
            return None

        prompt = f"{self.preprompt}: {message}"
        try:
            return self.provider.process_message(prompt, max_retries)
        except Exception as e:
            logger.error(f"error processing message: {e}")
            raise

    def needs_update(self, new_config):
        return self.provider_config != new_config

    def cleanup(self):
        try:
            if self.provider:
                if isinstance(self.provider, OllamaProvider):
                    logger.debug("closing ollama provider session")
                    if hasattr(self.provider, "session"):
                        self.provider.session.close()

                if isinstance(self.provider, MetaAIProvider):
                    if hasattr(self.provider, "bot"):
                        self.provider.bot = None

            logger.debug("ai instance cleanup completed")
        except Exception as e:
            logger.error(f"error during ai cleanup: {e}", exc_info=True)

        self.provider = None
