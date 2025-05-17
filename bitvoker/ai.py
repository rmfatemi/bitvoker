from meta_ai_api import MetaAI

from bitvoker.utils import truncate
from bitvoker.logger import setup_logger


logger = setup_logger("ai")


class AI:
    def __init__(self, preprompt):
        self.preprompt = preprompt
        self.bot = MetaAI()

    def process_message(self, message, max_retries=3):
        prompt = f"{self.preprompt}: {message}"

        retry_count = 0
        while retry_count <= max_retries:
            try:
                response = self.bot.prompt(prompt)
                result = response["message"]
                logger.debug("ai processed message result: %s", truncate(result, 80))
                return result
            except Exception as e:
                retry_count += 1
                logger.warning(f"ai processing attempt {retry_count} failed: {e}")
                if retry_count > max_retries:
                    logger.error("all ai processing attempts failed")
                    raise RuntimeError(f"failed to process message after {max_retries} retries") from e
                try:
                    self.bot = MetaAI()
                except Exception as init_error:
                    logger.error(f"failed to recreate ai connection: {init_error}")
