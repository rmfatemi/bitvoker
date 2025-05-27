import requests

from meta_ai_api import MetaAI

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


logger = setup_logger("ai")


class MetaAIProvider:
    def __init__(self):
        self.bot = MetaAI()

    def process_message(self, prompt, max_retries=3):
        for retry_count in range(max_retries):
            try:
                response = self.bot.prompt(prompt)
                result = response["message"]
                logger.debug(f"meta-ai processed message: {truncate(result, 80)}")
                return result
            except Exception as e:
                logger.warning(f"meta-ai processing attempt {retry_count + 1} failed: {e}")
                try:
                    self.bot = MetaAI()
                except Exception as init_error:
                    logger.error(f"failed to recreate meta-ai connection: {init_error}")

        logger.error("all meta-ai processing attempts failed")
        raise RuntimeError(f"failed to process message after {max_retries} retries")


class OllamaProvider:
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
                error_msg = f"model '{self.model}' not found in ollama."
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


def process_with_ai(message, preprompt, ai_config, max_retries=3):
    if not ai_config:
        logger.warning("no ai config provided")
        return None

    try:
        provider = get_provider(ai_config)
        prompt = f"{preprompt}: {message}"
        result = provider.process_message(prompt, max_retries)

        if isinstance(provider, OllamaProvider) and hasattr(provider, "session"):
            provider.session.close()

        return result
    except Exception as e:
        logger.error(f"error processing message with ai: {e}")
        raise


def get_provider(ai_config):
    provider_type = ai_config.get("provider", "meta_ai")
    if provider_type == "ollama":
        logger.info("using ollama as ai provider")
        ollama_config = ai_config.get("ollama", {})
        url = ollama_config.get("url", "http://localhost:11434")
        model = ollama_config.get("model", "gemma3:1b")
        return OllamaProvider(url=url, model=model)
    else:
        logger.info("using meta-ai as ai provider")
        return MetaAIProvider()
