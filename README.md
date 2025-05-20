
<p align="center">
  <img src="https://github.com/user-attachments/assets/f2fa251e-0038-47b8-8b2e-d693eb38106f" width="500">
</p>



**bitvoker** is an open-source, dynamic notification system designed to streamline automated alerts in both homelab setups and production environments. It operates via a dedicated TCP server that accepts messages and, if enabled, can refine them using AI-generated summaries before dispatching notifications through multiple channels such as Telegram, Discord, Slack, and more.

## Features

- 🌐 **Multi-Channel Support**: Send notifications to:
    <ul>
      <li>
        <span style="background-color: #039be5; color: white; padding: 2px; border-radius: 5px;">
          <img src="https://github.com/rmfatemi/bitvoker/blob/d9e4136baf0ddfeb3ec06e79c7888005d6a39fc3/web/src/assets/telegram.svg" width="15" style="vertical-align: middle;"> Telegram
        </span>
      </li>
      <li>
        <span style="background-color: #7289da; color: white; padding: 2px; border-radius: 5px;">
          <img src="https://github.com/rmfatemi/bitvoker/blob/d9e4136baf0ddfeb3ec06e79c7888005d6a39fc3/web/src/assets/discord.svg" width="15" style="vertical-align: middle;"> Discord
        </span>
      </li>
      <li>
        <span style="background-color: #4a154b; color: white; padding: 2px; border-radius: 5px;">
          <img src="https://github.com/rmfatemi/bitvoker/blob/d9e4136baf0ddfeb3ec06e79c7888005d6a39fc3/web/src/assets/slack.svg" width="15" style="vertical-align: middle;"> Slack
        </span>
      </li>
      <li>
        <span style="background-color: #3498db; color: white; padding: 2px; border-radius: 5px;">
          <img src="https://github.com/rmfatemi/bitvoker/blob/d9e4136baf0ddfeb3ec06e79c7888005d6a39fc3/web/src/assets/gotify.svg" width="15" style="vertical-align: middle;"> Gotify
        </span>
      </li>
    </ul>

- 🤖 **Optional AI Processing**: Enhance messages by summarizing notifications using customizable pre-prompts.
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 🖥️ **Web Dashboard**: User-friendly interface for configuration and notification management
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels
- ⚙️ **Dynamic Configuration**: Update settings without restarting the server
- 📊 **Detailed Logging**: Logging system accessible via web interface

## AI Summaries

**bitvoker** offers an optional AI-powered enhancement to refine and summarize notifications. You can tailor the alert content to your exact needs. Not only can you enable this feature through unauthenticated interactions with Meta's LLAMA4 model or through local self-hosting with Ollama, but you can also customize the pre-prompts that guide the AI's summarization process. This lets you define specific instructions and contextual cues for how notifications should be summarized. There are two supported configurations:

1. **Unauthenticated Access to Meta's LLAMA4**:  
   By default, bitvoker can connect to [Meta's LLAMA4](https://www.meta.ai/) model via unauthenticated API calls. This method simplifies setup and provides out-of-the-box enhancements, though it is subject to API rate limits and regional availability.

2. **Self-Hosted AI Processing with Ollama**:  
   For users who prioritize complete data privacy or wish to avoid potential external usage limits, bitvoker supports local AI processing with [Ollama](https://ollama.com/). This solution allows you to deploy a model such as `gemma3:1b`, which we recommend as a compact yet powerful option that performs well even on limited hardware.

>[!WARNING]
> If privacy or independence from third-party services is a priority, the self-hosted Ollama option is recommended. Additionally, users encountering rate limits or availability issues with Meta’s service may opt for the local AI processing solution. The AI summary feature is disabled by default, and you can choose the most suitable configuration based on your needs.

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
#### Prerequisites

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

2. **Aggregated System Health Check:**
    Combine multiple system metrics into one comprehensive update:
    ```bash
    */5 * * * * (echo "System Health at $(date):" && \
    echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4 \"%\"}')" && \
    echo "Memory Usage:" && free -h && \
    echo "Disk Usage:" && df -h) | openssl s_client -connect <server-ip>:8084
    ```

3. **Log Monitoring Alert (Event-Driven):**
    Monitor a log file for errors and trigger notifications when issues occur:
    ```bash
    tail -F /var/log/application.log | grep --line-buffered "error" | while read -r line; do
      echo "Alert: $line (detected at $(date))" | openssl s_client -connect <server-ip>:8084
    done
    ```

4. **Docker Event Notification:**
    Pipe Docker events directly to **bitvoker**:
    ```bash
    docker events --filter 'event=start' --filter 'event=stop' | while read event; do
      echo "Docker Event: $event" | openssl s_client -connect <server-ip>:8084
    done
    ```

5. **Custom Aggregated Alert Script:**
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

6. **Website Content Monitoring:**
 Monitor a webpage for specific content (e.g., a deal or release) and trigger an alert through **bitvoker**. For example, use this minimal Bash script:
    ```bash
    #!/bin/bash
    # /usr/local/bin/bitvoker-cron.sh
    # This script fetches Microcenter's Specials page, prepends an AI pre-prompt,
    # and sends it to Bitvoker.
    URL="https://www.microcenter.com/site/specials.aspx"
    SERVER_IP="your.server.ip"      # Replace with your Bitvoker server IP
    PORT="8083"                     # Use 8084 for TLS
    
    PREPROMPT="Summarize and extract any notable computer component deals from the text below:"
    PAGE_CONTENT=$(curl -s "$URL")
    MESSAGE="${PREPROMPT}\n\n${PAGE_CONTENT}"
    echo -e "$MESSAGE" | nc $SERVER_IP $PORT
    ```
Then make it executable `chmod +x /usr/local/bin/bitvoker-cron.sh` and add your cronjob `*/10 * * * * /usr/local/bin/bitvoker-cron.sh`

These examples illustrate just a portion of the creative ways you can integrate **bitvoker** into your environment. By chaining and piping various system commands, you can engineer powerful, automated notifications tailored to your specific homelab or production needs.

### Web Interface
Access the web interface at `http://<server-ip>:8085` to:
- View notification history
- Configure notification channels
- Adjust AI settings
- View system logs

### Main dashboard

<img src="https://github.com/user-attachments/assets/402b1394-6d29-4d6e-8720-095fc123a7bd">



### Settings and configurations

<img src="https://github.com/user-attachments/assets/b8d01264-4eb8-4cfb-afca-f86e1eae7d1a">







## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rmfatemi/bitvoker/blob/master/LICENSE) file for details.
