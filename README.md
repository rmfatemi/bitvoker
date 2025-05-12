<p align="center">
  <img src="https://github.com/user-attachments/assets/2b2ed949-fa68-4de4-83c7-546067cfd8ba" width="500">
</p>

**bitvoker** is an open-source, versatile AI notification system that receives messages via a TCP server, processes them optionally with AI-generated summaries, and dispatches notifications across multiple channels.

## Features

- 🌐 **Multi-Channel Support**: Send notifications to:
  - Telegram
  - Discord
  - Slack
  - Gotify
- 🤖 **AI Processing**: Optional message enhancement powered by [Meta.AI](https://www.meta.ai/) that refines and summarizes notifications with customizable pre-prompts.
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 🖥️ **Web Dashboard**: User-friendly Flask interface for configuration and notification management
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels
- 📊 **Detailed Logging**: Logging system accessible via web interface
- ⚡ **Dynamic Configuration**: Update settings without restarting the server

## Setup
This repository supports two ways of running **bitvoker**. For a consistent and isolated environment, **using Docker is recommended**.

### Using Docker (Recommended)

#### Docker CLI

You can run the Docker container directly. If the image is not present locally, Docker will automatically pull it from the registry.

   ```bash
   mkdir -p docker-tmp-data
   docker run --rm -p 8084:8084 -p 8085:8085 -v $(pwd)/docker-tmp-data:/app/data --name bitvoker [tba]/bitvoker
   ```
The application will be accessible on ports 8084 for server and 8085 for web GUI.

#### Docker Compose

Create a docker-compose.yaml file copy the following inside it:

```
services:
  bitvoker:
    image: [tba]/bitvoker
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

Send messages to **bitvoker**'s TCP server to trigger notifications. Below are some examples:

1. Automated Rsync Backup Notification (Cron Job):
```bash
# Run daily at 2:00 AM:
0 2 * * * rsync -avh /path/to/source /path/to/backup && echo "Backup complete at $(date)" | nc <server-ip> 8084
```
2. Uptime Monitoring (Cron Job):
```bash
# Every 30 minutes:
*/30 * * * * uptime | nc <server-ip> 8084
```
3. Weather Update Notification (Cron Job):
```bash
# Every hour:
0 * * * * curl -s "http://wttr.in/?format=3" | nc <server-ip> 8084
```
4. Disk Space Notification (Cron Job):
```bash
# Every 15 minutes:
*/15 * * * * df -h | nc <server-ip> 8084
```
5. Memory Usage Notification (Cron Job):
```bash
# Every 10 minutes:
*/10 * * * * free -h | nc <server-ip> 8084
```
6. System Load Notification (Cron Job):
```bash
# Every 10 minutes:
*/10 * * * * top -bn1 | grep "load average:" | nc <server-ip> 8084
```
7. File Modification Trigger (Event-Based):
```bash
# Trigger a notification when a specific file changes:
inotifywait -e modify /path/to/monitored/file && echo "File modified at $(date)" | nc <server-ip> 8084
```
8. Service Status Alert (Triggered):
```bash
# Trigger a notification when a specific file changes:
inotifywait -e modify /path/to/monitored/file && echo "File modified at $(date)" | nc <server-ip> 8084
```

### Web Interface

Access the web interface at `http://<server-ip>:8085` to:
- View notification history
- Configure notification channels
- View system logs
- Adjust AI settings

#### Main dashboard
  ![image](https://github.com/user-attachments/assets/7b8884b5-f4d9-47b5-8988-c04b49708c78)


#### Settings and configurations
  ![image](https://github.com/user-attachments/assets/04306a72-8f83-4d42-b280-994aed72d69f)


#### Light mode
  ![image](https://github.com/user-attachments/assets/edce9c46-1c44-4347-9602-fbf7e46a0180)

#### Telegram notifcation
  <img src="https://github.com/user-attachments/assets/ba10c5a5-3bd4-4340-a973-7f2986b26c61" width="300">

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rmfatemi/bitvoker/blob/master/LICENSE) file for details.
