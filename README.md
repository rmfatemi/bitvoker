# Bitvoker 🤖🚀

Bitvoker is an open source project that listens for incoming messages via a socket server, processes them using optional AI-enhanced techniques, and then sends them to Telegram. It comes with a flexible configuration system and detailed logging to help you monitor its activity.

## Features ⚙️

- **Modular Design:** Organized into distinct components: AI processing, configuration, Telegram integration, and server management.
- **Configurable Options:** Toggle AI processing and display of original messages in a single configuration file.
- **Easy Setup:** Just edit `config.yaml` to customize settings like server host, port, Telegram bot credentials, and more.
- **Robust Logging:** Integrated logging makes it easy to track activity and troubleshoot issues.

## Requirements 📦

- Python 3.7 or higher
- [PyYAML](https://pypi.org/project/PyYAML/)
- [Requests](https://pypi.org/project/requests/)

## Configuration 🔧

Edit the `config.yaml` file in the project root. Here's an example configuration:

```yaml
bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
chat_id: "YOUR_TELEGRAM_CHAT_ID"
preprompt: |
  Welcome! This is your AI preprompt.
enable_ai: true
show_original: true
server_host: ""     # Leave empty to listen on all interfaces
server_port: 9090   # Default server port
```

- **bot_token:** Your Telegram bot token.
- **chat_id:** The Telegram chat ID where messages will be sent.
- **preprompt:** The initial text prepended to messages for AI processing.
- **enable_ai:** Set to `true` to activate AI processing.
- **show_original:** Set to `true` to include the original message along with AI output.
- **server_host:** An empty string (`""`) binds the server to all available network interfaces.
- **server_port:** The default port (9090) where the server listens; override as needed.

## Usage 🚀

### Running the Server

To start the server, run:

```bash
python -m bitvoker.server
```

The server will bind to the specified host and port, process incoming messages according to your configuration, and forward them to the designated Telegram chat.

### Running in the Background 🌙

Run the server in the background using `nohup`:

```bash
nohup python -m bitvoker.server &
```

Or use process manager tools like `systemd` or `pm2`.

### Stopping the Server 🚦

If running in the foreground, press `Ctrl + C` to stop the server. If running in the background, find its process ID:

```bash
ps aux | grep bitvoker.server
```

Then kill the process:

```bash
kill <PID>
```

## Contributing 🤝

Contributions are welcome! Open issues or pull requests on GitHub.

## License 🔓

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
