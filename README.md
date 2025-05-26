<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/rmfatemi/bitvoker/master/web/src/assets/bitvoker.svg" width="500"></td>
    <td><strong>bitvoker</strong> is an open-source, adaptable notification system engineered to optimize automated alerts from homelab environments to production infrastructures. It functions through a dedicated TCP server that ingests incoming messages. Optionally, these messages can be refined into heavily customizable rule-based AI-generated summaries before being dispatched through various integrated channels, including Slack, Discord, and Microsoft Team.</td>
  </tr>
</table>


## Features

- 📢 **Multi-platform support**:
  <p>
  <span>
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/telegram.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/slack.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/microsoft-teams.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/gmail.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/discord.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/whatsapp.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/gotify.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/ntfy.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/pushover.svg" width="20">
    <img src="https://github.com/homarr-labs/dashboard-icons/blob/main/svg/home-assistant.svg" width="20">
  </span> 
   for seamless notifications and many more thanks to Apprise integration.
</p>

- 🤖 **Customizable AI Processing**: Refine messages by summarizing notifications using customizable pre-prompts.
- ☁️ **Cloud and Self-Hostable AI**: Choose between Meta’s LLAMA4 for cloud-based processing or Ollama for privacy
- 📜 **Notification History**: Store and browse past notifications with timestamps and source information
- 🖥️ **Web Dashboard**: Modern interface for configuration and notification management
- 🔄 **Real-time Updates**: Instantly receive notifications across all configured channels
- ⚙️ **Dynamic Configuration**: Update settings without restarting the server
- 📊 **Detailed Logging**: Logging system accessible via web interface

## AI Processing

**bitvoker** offers advanced AI-powered notification processing with fully customizable rules. This feature enables you to refine, summarize, and tailor notifications to your specific requirements by applying detailed matching conditions.

You can enable AI processing through unauthenticated interactions with Meta's LLAMA4 model or by self-hosting with Ollama. Define **pre-prompts** to dynamically guide AI behavior, and use the new rule system for granular control over how and when AI processing occurs.

---

### Flexible AI Processing Deployment

1.  **Unauthenticated Access to Meta's LLAMA4**:
    By default, **bitvoker** can connect to <a href="https://www.meta.ai/">Meta's LLAMA4</a> model via unauthenticated API calls. This offers straightforward setup and immediate integration, though it is subject to API rate limits and regional availability.
    
>[!TIP]
> Users experiencing rate limits or availability issues with Meta’s service can either switch to the local AI processing or reduce/disable AI queries as needed.

2.  **Self-Hosted AI Processing with Ollama**:
    For users prioritizing data privacy or looking to bypass external usage limits, **bitvoker** supports local AI processing with <a href="https://ollama.com/">Ollama</a>. We recommend deploying a compact yet powerful model like `gemma3:1b` for optimal performance, even on systems with limited hardware. Users requiring enhanced privacy, stricter control, or wishing to avoid external rate limits are advised to opt for the self-hosted Ollama configuration
---

### Advanced Notification Rule System

**bitvoker**'s rule system provides complete control over notification processing and delivery:

* **Customizable Behavior**: Define rules to cutomize alerts based on source of alert, original content, AI prcessed content and more
* **Dynamic Notification Delivery**: Complete control over notification destinations, including when, where, and what to send
* **Granular Control**: Maintain full control over sources, destinations, and AI behavior while preserving adaptable automation workflows.
---

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
