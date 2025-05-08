from meta_ai_api import MetaAI

class AI:
    def __init__(self, preprompt):
        self.preprompt = preprompt
        self.bot = MetaAI()

    def process_message(self, message):
        prompt = f"{self.preprompt}: {message}"
        response = self.bot.prompt(prompt)
        return response["message"]
