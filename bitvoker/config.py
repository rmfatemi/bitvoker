import os
import yaml

class Config:
    def __init__(self, filename="config.yaml"):
        self.filename = filename
        self.config_data = self._load_config()

    def _load_config(self):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(pkg_dir, os.pardir))
        config_path = os.path.join(root_dir, self.filename)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file '{config_path}' not found.")
        with open(config_path, "r", encoding="utf-8") as config_file:
            try:
                data = yaml.safe_load(config_file) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing config file: {e}") from e
        return data

    @property
    def bot_token(self):
        token = self.config_data.get("bot_token")
        if not token:
            raise KeyError("Missing 'bot_token'")
        return token

    @property
    def chat_id(self):
        cid = self.config_data.get("chat_id")
        if not cid:
            raise KeyError("Missing 'chat_id'")
        return cid

    @property
    def preprompt(self):
        prompt = self.config_data.get("preprompt")
        if not prompt:
            raise KeyError("Missing 'preprompt'")
        return prompt

    @property
    def enable_ai(self):
        return self.config_data.get("enable_ai", True)

    @property
    def show_original(self):
        return self.config_data.get("show_original", True)

    @property
    def server_host(self):
        return self.config_data.get("server_host", "")

    @property
    def server_port(self):
        return self.config_data.get("server_port", 9090)
