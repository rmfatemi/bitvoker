import os
import yaml

class Config:

    def __init__(self, filename: str = "config.yaml"):
        self.filename = filename
        self.config_data = self._load_config()

    def _load_config(self) -> dict:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, self.filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file '{config_path}' not found.")

        with open(config_path, "r", encoding="utf-8") as config_file:
            try:
                data = yaml.safe_load(config_file) or {}
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error reading the YAML file: {e}")

        return data

    @property
    def bot_token(self) -> str:
        token = self.config_data.get("bot_token")
        if not token:
            raise KeyError("The configuration is missing the 'bot_token' key.")
        return token

    @property
    def chat_id(self) -> str:
        cid = self.config_data.get("chat_id")
        if not cid:
            raise KeyError("The configuration is missing the 'chat_id' key.")
        return cid

    @property
    def preprompt(self) -> str:
        prompt = self.config_data.get("preprompt")
        if not prompt:
            raise KeyError("The configuration is missing the 'preprompt' key.")
        return prompt
