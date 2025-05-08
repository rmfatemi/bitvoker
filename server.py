import socketserver
from config import Config
from telegram import Telegram
from ai import AI
from handler import Handler

def main():
    config = Config()
    telegram = Telegram(config.bot_token, config.chat_id)
    ai = AI(config.preprompt)
    HOST, PORT = "", 9090
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as server:
        server.telegram = telegram
        server.ai = ai
        print(f"Server listening on port {PORT} ...")
        server.serve_forever()

if __name__ == "__main__":
    main()
