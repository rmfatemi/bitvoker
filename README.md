<p align="center">
  <img src="https://github.com/user-attachments/assets/2b2ed949-fa68-4de4-83c7-546067cfd8ba" width="500">
</p>

**bitvoker** is an open-source, dynamic notification system built to streamline automated alerts in both homelab setups and production environments. It operates via a dedicated TCP server that accepts messages and can optionally refine them with AI-generated summaries before dispatching notifications through multiple channels such as Telegram, Discord, Slack, and more.

## Features

- 🌐 **Multi-Channel Support**: Send notifications to:
  - Telegram
  - Discord
  - Slack
  - Gotify
- 🤖 **AI Processing**: Optional message enhancement that refines and summarizes notifications with customizable pre-prompts.
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 🖥️ **Web Dashboard**: User-friendly interface for configuration and notification management
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels
- ⚡ **Dynamic Configuration**: Update settings without restarting the server
- 📊 **Detailed Logging**: Logging system accessible via web interface

>[!WARNING]
> The AI summary is provided through unauthenticated interactions with Meta's AI APIs on the backend of [Meta AI](https://www.meta.ai/). Although this unauthenticated access results in improved privacy, if you truly prefer complete privacy, you must disable this option. It is disabled by default.
> The AI summary feature is not available in all regions due to [Meta AI](https://www.meta.ai/)'s regional limitations.

>[!TIP]
> Unauthenticated prompts are subject to usage limits. If you are sending hundreds of notifications per day to **bitvoker**, it is recommended that you disable the AI feature when you encounter a rate limit. Support for selective AI summary to help avoid this issue will be available in a future release.

## Setup
This repository supports two ways of running **bitvoker**. For a consistent and isolated environment, using Docker is recommended.

### Docker

Create a `docker-compose.yaml` file copy the following inside it:

```
services:
  bitvoker:
    image: ghcr.io/rmfatemi/bitvoker:latest
    container_name: bitvoker
    ports:
      - "8083:8083"    # plain text tcp server
      - "8084:8084"    # secure tcp server
      - "8085:8085"    # web ui
    volumes:
      - bitvoker_data:/app/data
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped

volumes:
  bitvoker_data:
    name: bitvoker_data
```
Then start the service with:
```
docker-compose up -d
```
### Standalone Installation
### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager
- [GNU Make](https://www.gnu.org/software/make/) utility
  -    `sudo apt-get install make` (Debian-based Linux), or `brew install make` (macOS)
1. Clone the repository:
    ```bash
    git clone https://github.com/rmfatemi/bitvoker.git
    cd bitvoker
    ```

2. Install dependencies:
    ```bash
    make install
    ```

3. Run the application:
    ```bash
    poetry run bitvoker
    ```


## 📖 Usage

Send messages to **bitvoker**’s notification endpoint using nc (netcat) or openssl for secure connections.

#### Plain text connection (Port 8083):

Using `nc`: `echo "Your notification message" | nc <server-ip> 8083`

#### Secure connection with TLS (Port 8084):

Using `openssl`: `echo "Your notification message" | openssl s_client -connect <server-ip>:8084`

**bitvoker** is designed for both automated recurring notifications and one-time alerts. Below are some creative usage scenarios:

1. **Daily Automated Rsync Backup Notification (Cron Job):**
    ```bash
    0 2 * * * rsync -avh /path/to/source /path/to/backup && echo "Backup complete at $(date)" | openssl s_client -connect <server-ip>:8084
    ```

2. **Uptime Monitoring (Cron Job):**
    ```bash
    */30 * * * * uptime | nc <server-ip> 8083
    ```

3. **Hourly Weather Update Notification (Cron Job):**
    ```bash
    0 * * * * curl -s "http://wttr.in/?format=3" | nc <server-ip> 8083
    ```

4. **Aggregated System Health Check:**
    Combine multiple system metrics into one comprehensive update:
    ```bash
    */5 * * * * (echo "System Health at $(date):" && \
    echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4 \"%\"}')" && \
    echo "Memory Usage:" && free -h && \
    echo "Disk Usage:" && df -h) | openssl s_client -connect <server-ip>:8084
    ```

5. **Log Monitoring Alert (Event-Driven):**
    Monitor a log file for errors and trigger notifications when issues occur:
    ```bash
    tail -F /var/log/application.log | grep --line-buffered "error" | while read -r line; do
      echo "Alert: $line (detected at $(date))" | openssl s_client -connect <server-ip>:8084
    done
    ```

6. **Docker Event Notification:**
    Pipe Docker events directly to **bitvoker**:
    ```bash
    docker events --filter 'event=start' --filter 'event=stop' | while read event; do
      echo "Docker Event: $event" | openssl s_client -connect <server-ip>:8084
    done
    ```

7. **External IP Address Change Alert:**
    Monitor for changes in your public IP by using **bitvoker** in a script:
    ```bash
    #!/bin/bash
    LAST_IP_FILE="/tmp/last_ip.txt"
    CURRENT_IP=$(curl -s https://api.ipify.org)
    LAST_IP=$(cat "$LAST_IP_FILE" 2>/dev/null)

    if [ "$CURRENT_IP" != "$LAST_IP" ]; then
        echo "External IP updated to: $CURRENT_IP at $(date)" | nc <server-ip>:8083
        echo "$CURRENT_IP" > "$LAST_IP_FILE"
    fi
    ```

8. **Custom Aggregated Alert Script:**
    Create a custom script that aggregates several checks and sends a notification only if issues are detected. Save the following as `healthcheck.sh` and schedule it via cron:
    ```bash
    #!/bin/bash
    LAST_IP_FILE="/tmp/last_ip.txt"
    CURRENT_IP=$(curl -s https://api.ipify.org)
    LAST_IP=$(cat "$LAST_IP_FILE" 2>/dev/null)

    if [ "$CURRENT_IP" != "$LAST_IP" ]; then
        echo "External IP updated to: $CURRENT_IP at $(date)" | openssl s_client -connect <server-ip>:8084
        echo "$CURRENT_IP" > "$LAST_IP_FILE"
    fi
    ```
    And add to cron:
    ```bash
    */15 * * * * /path/to/healthcheck.sh
    ```

These examples illustrate just a portion of the creative ways you can integrate **bitvoker** into your environment. By chaining and piping various system commands, you can engineer powerful, automated notifications tailored to your specific homelab or production needs.

### Web Interface

Access the web interface at `http://<server-ip>:8085` to:
- View notification history
- Configure notification channels
- Adjust AI settings
- View system logs

#### Main dashboard
  <img src="https://github.com/user-attachments/assets/57c67819-091b-4963-aed6-9bfb2f523ae5" width="1200">


#### Settings and configurations
  <img src="https://github.com/user-attachments/assets/eb8ef1be-e44c-4943-9214-209e1915e403" width="1200">

#### Light mode
  <img src="https://github.com/user-attachments/assets/06b1fce3-a88b-4c10-a44f-e71d731e4bae" width="1200">

#### Telegram notifcation
  <img src="https://github.com/user-attachments/assets/ba10c5a5-3bd4-4340-a973-7f2986b26c61" width="300">

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rmfatemi/bitvoker/blob/master/LICENSE) file for details.
