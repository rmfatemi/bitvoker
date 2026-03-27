<p>
  <img align="left" src="https://raw.githubusercontent.com/rmfatemi/bitvoker/master/web/src/assets/bitvoker.svg" width="100" />
  <strong>bitvoker</strong> is a notification system that receives raw messages over TCP, filters and processes them through customizable rules and optional AI, then delivers them to over 100 destinations including Slack, Discord, Telegram, Microsoft Teams, Email, and more via <a href="https://github.com/caronc/apprise">Apprise</a>.
</p>
<br>

## What Does It Do?

<strong>bitvoker</strong> turns raw text into targeted, intelligent alerts. Send it logs, text, or any data, and configure rules to control exactly what happens. With regex matching and AI processing, here are some examples:

1. Security logs from `web-gateway-03` contain `Failed login attempt` for user `admin` from an IP outside `192.168.1.0/24`, use a local LLM to identify the attack origin and recommend action, then send only the AI summary to the SOC team's Slack channel.

2. A scraped product page contains `Sony WH-1000XM5` with a discount over 15%, extract the current price, original price, and buy link using AI, then send the deal to a Telegram chat.

3. Database logs from `db-prod-01` show `long_query_threshold` exceeded over `1000ms`, summarize the impact using Meta's LLAMA4, send both the summary and the original log (only if it contains an IP starting with `10.0.0.`) to the DBA team's Microsoft Teams channel and email inbox.

## Features

- **Multi-platform support**: notifications for
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
   and many more thanks to <a href="https://github.com/caronc/apprise">Apprise</a> integration.
</p>

- **AI Processing**: refine messages using customizable pre-prompts with Meta's LLAMA4 or self-hosted Ollama
- **Flexible Rule System**: regex matching, source filtering, and per-rule AI and destination control
- **Web Dashboard**: modern interface for configuration, notification history, and log viewing
- **Authentication**: optional login for the web UI and token verification for TCP messages
- **Dynamic Configuration**: update settings and rules without restarting the server
- **Notification History**: browse and filter past notifications with timestamps and source info

## AI Processing

bitvoker can optionally process messages with AI before delivery:

- **Meta LLAMA4** (default): free cloud-based processing via [meta.ai](https://www.meta.ai/), subject to rate limits
- **Ollama**: self-hosted local processing via [ollama.com](https://ollama.com/), recommended for privacy and reliability

Define pre-prompts in your rules to control how AI processes each message. See the [wiki](https://github.com/rmfatemi/bitvoker/wiki) for the full rule reference.

> [!TIP]
> If you experience rate limits with Meta's service, switch to Ollama or reduce AI queries. A compact model like `gemma3:1b` works well even on limited hardware.

## Setup

### Docker (recommended)

```yaml
services:
  bitvoker:
    image: ghcr.io/rmfatemi/bitvoker:latest
    container_name: bitvoker
    # host mode recommended (see wiki for details)
    network_mode: host
    # for bridge mode, comment out the line above and uncomment below
    # ports:
    #   - "8083:8083" # TCP server
    #   - "8084:8084" # TLS server
    #   - "8085:8085" # Web UI HTTPS
    #   - "8086:8086" # Web UI HTTP
    volumes:
      - bitvoker_data:/app/data
      - /etc/localtime:/etc/localtime:ro
    environment:
      # Optional: uncomment to enable web UI login
      # - BITVOKER_USERNAME=admin
      # - BITVOKER_PASSWORD=changeme
    restart: unless-stopped

volumes:
  bitvoker_data:
    name: bitvoker_data
```

```shell
docker-compose up -d
```

### Standalone

Requires Python 3.11+ and [GNU Make](https://www.gnu.org/software/make/).

```bash
git clone https://github.com/rmfatemi/bitvoker.git
cd bitvoker
make install
make run
```

## Authentication

Set `BITVOKER_USERNAME` and `BITVOKER_PASSWORD` environment variables to enable login for the web UI. When not set, the UI is accessible without authentication.

For TCP messages, optionally configure a `message_token` in the settings to require authentication:

**Without token authentication** (default, if `message_token` is not set):
```
echo "your message" | nc {server_ip} 8083
```

**With token authentication** (if `message_token` is configured in settings):
```
echo "TOKEN:your_secret_token:your message" | nc {server_ip} 8083
```

Messages without the correct token prefix will be rejected when token authentication is enabled.

## Usage

Send messages to bitvoker over TCP using plaintext (port `8083`) or TLS (port `8084`).

```shell
echo "your notification" | nc {server_ip} 8083
```

```shell
echo "your notification" | openssl s_client -connect {server_ip}:8084
```

```python
import socket, ssl

context = ssl.create_default_context()
with socket.create_connection(("{server_ip}", 8084)) as sock:
    with context.wrap_socket(sock, server_hostname="{server_ip}") as s:
        s.sendall(b"your notification")
```

> [!TIP]
> If you're not comfortable with YAML and regular expressions, any AI model can help you create your rules — just provide it with the rule reference from the [wiki](https://github.com/rmfatemi/bitvoker/wiki) and describe what you need.

## Web Interface

Access the web UI at `https://{server_ip}:8085` (or `http` on port `8086`) to configure destinations, rules, AI settings, and view notification history and logs.

### Screenshots
<img src="https://github.com/user-attachments/assets/7d168752-ad8a-4230-b627-00cc7c7bb601">
<img src="https://github.com/user-attachments/assets/4e64c12b-5db5-4ae7-ba7d-344bd427c318">
<img src="https://github.com/user-attachments/assets/4576d1d9-7f9b-4be3-9be5-69774ab980f1">
<img src="https://github.com/user-attachments/assets/ced0b8ae-25cd-4d51-addd-ba38f7b65e1a">

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rmfatemi/bitvoker/blob/master/LICENSE) file for details.
