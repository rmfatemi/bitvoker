import requests

class Telegram:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, message):
        payload = {"chat_id": self.chat_id, "text": message}
        response = requests.post(self.api_url, data=payload)
        if not response.ok:
            raise Exception("Failed to send message: " + response.text)
        return response.json()
