<p>
  <img align="left" src="https://raw.githubusercontent.com/rmfatemi/bitvoker/master/web/src/assets/bitvoker.svg" width="100" />
  <strong>bitvoker</strong> is a notification system that receives raw messages over TCP, filters and processes them through customizable rules and optional AI, then delivers them to over 100 destinations including Slack, Discord, Telegram, Microsoft Teams, Email, and more via <a href="https://github.com/caronc/apprise">Apprise</a>.
</p>
<br>

## Features

- **100+ notification destinations** via Apprise (Slack, Discord, Telegram, Teams, Email, etc.)
- **AI processing** with customizable pre-prompts using Meta LLAMA4 or self-hosted Ollama
- **Flexible rule system** with regex matching, source filtering, and per-rule AI and destination control
- **Web dashboard** for configuration, notification history, and log viewing
- **Authentication** for the web UI and TCP message token verification
- **Dynamic configuration** without server restarts

## AI Processing

bitvoker can optionally process messages with AI before delivery. Two providers are supported:

- **Meta LLAMA4** (default) - free cloud-based processing via [meta.ai](https://www.meta.ai/), subject to rate limits
- **Ollama** - self-hosted local processing via [ollama.com](https://ollama.com/), recommended for privacy and reliability

Define pre-prompts in your rules to control how AI processes each message. See the [wiki](https://github.com/rmfatemi/bitvoker/wiki) for rule configuration details.

## Setup

### Docker (recommended)

```yaml
services:
  bitvoker:
    image: ghcr.io/rmfatemi/bitvoker:latest
    container_name: bitvoker
    network_mode: host
    # for bridge mode, comment out the line above and uncomment below
    # ports:
    #   - "8083:8083"
    #   - "8084:8084"
    #   - "8085:8085"
    #   - "8086:8086"
    volumes:
      - bitvoker_data:/app/data
      - /etc/localtime:/etc/localtime:ro
    environment:
      - BITVOKER_USERNAME=admin
      - BITVOKER_PASSWORD=changeme
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

For TCP messages, configure a `message_token` in the settings to require a token prefix on incoming messages:

```
TOKEN:your_secret:your message here
```

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

## Web Interface

Access the web UI at `https://{server_ip}:8085` (or `http` on port `8086`) to configure destinations, rules, AI settings, and view notification history and logs.

### Screenshots
<img src="https://github.com/user-attachments/assets/7d168752-ad8a-4230-b627-00cc7c7bb601">
<img src="https://github.com/user-attachments/assets/4e64c12b-5db5-4ae7-ba7d-344bd427c318">
<img src="https://github.com/user-attachments/assets/4576d1d9-7f9b-4be3-9be5-69774ab980f1">
<img src="https://github.com/user-attachments/assets/ced0b8ae-25cd-4d51-addd-ba38f7b65e1a">

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/rmfatemi/bitvoker/blob/master/LICENSE) file for details.
