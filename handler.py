import socketserver

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        message = data.decode("utf-8")
        print("Received:", message)
        if hasattr(self.server, "ai"):
            try:
                message = self.server.ai.process_message(message)
            except Exception as e:
                print("Error processing message through AI:", e)
        if hasattr(self.server, "telegram"):
            try:
                self.server.telegram.send_message(message)
            except Exception as e:
                print("Error sending telegram message:", e)
