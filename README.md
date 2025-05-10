# Bitvoker 🔔

Bitvoker is an open-source, versatile notification system that receives messages via a TCP server, processes them optionally with AI, and dispatches notifications across multiple channels.

## ✨ Features

- 🌐 **Multi-Channel Support**: Send notifications to:
  - Telegram
  - Discord
  - Slack
  - Gotify
- 🤖 **AI Processing**: Optional message enhancement via OpenAI to summarize and improve notifications
- 🖥️ **Web Dashboard**: User-friendly Flask interface for configuration and notification management
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 📊 **Detailed Logging**: Comprehensive logging system accessible via web interface
- ⚡ **Dynamic Configuration**: Update settings without restarting the server
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels

## 📱 Supported Apps

Bitvoker supports sending notifications to:

- **Telegram**: The popular messaging app with bot capabilities
- **Discord**: Communication platform used by many communities
- **Slack**: Business communication platform
- **Gotify**: Self-hosted push notification service

Each integration is configurable through the web interface or directly in the YAML configuration file.


## 🚀 Installation

### Prerequisites

- Python 3.8.1 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bitvoker.git
cd bitvoker
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Run the application:
```bash
poetry run bitvoker
```

## 📖 Usage

### TCP Server

Send messages to the Bitvoker TCP server to trigger notifications:

```bash
echo "Your notification message" | nc localhost 8084
```

### Web Interface

Access the web interface at `http://localhost:5000` to:
- View notification history
- Configure notification channels
- View system logs
- Adjust AI settings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
