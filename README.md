# bitvoker

bitvoker is an open-source, versatile notification system that receives messages via a TCP server, processes them optionally with AI, and dispatches notifications across multiple channels.

## ✨ Features

- 🌐 **Multi-Channel Support**: Send notifications to:
  - Telegram
  - Discord
  - Slack
  - Gotify
- 🤖 **AI Processing**: Optional message enhancement via OpenAI to summarize and improve notifications
- 🖥️ **Web Dashboard**: User-friendly Flask interface for configuration and notification management
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 📊 **Detailed Logging**: Logging system accessible via web interface
- ⚡ **Dynamic Configuration**: Update settings without restarting the server
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels

## 🚀 Installation

## Setup
This repository supports two ways of running bitvoker. For a consistent and isolated environment, **using Docker is recommended**.

---

### Using Docker (Recommended)

#### Docker CLI

You can run the Docker container directly. If the image is not present locally, Docker will automatically pull it from the registry.

1. **Run the Docker container:**

   ```bash
   mkdir -p docker-tmp-data
   docker run --rm -p 8084:8084 -p 8085:8085 -v $(pwd)/docker-tmp-data:/app/data --name bitvoker [tba]/bitvoker
The application will be accessible on ports 8084 and 8085.

### Docker Compose

Create a docker-compose.yaml file copy the following inside it:

```
services:
  bitvoker:
    image: yourusername/bitvoker
    container_name: bitvoker
    ports:
      - "8084:8084"
      - "8085:8085"
    volumes:
      - ./docker-tmp-data:/app/data
    restart: unless-stopped
```

### Non-Docker Setup
### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager
1. Clone the repository:
    ```bash
    git clone https://github.com/rmfatemi/bitvoker.git
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

Send messages to the bitvoker TCP server to trigger notifications:

```bash
echo "Your notification message" | nc localhost 8084
```

### Web Interface

Access the web interface at `http://<server-ip>:8084` to:
- View notification history
- Configure notification channels
- View system logs
- Adjust AI settings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
