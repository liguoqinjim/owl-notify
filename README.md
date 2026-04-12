# owl-notify

[![PyPI version](https://img.shields.io/pypi/v/owl-notify)](https://pypi.org/project/owl-notify/)
[![Python](https://img.shields.io/pypi/pyversions/owl-notify)](https://pypi.org/project/owl-notify/)
[![License](https://img.shields.io/pypi/l/owl-notify)](https://github.com/liguoqinjim/owl-notify/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/owl-notify)](https://pepy.tech/project/owl-notify)

A simple notification CLI for Bark, Weixin, and custom webhooks.

## Installation

```bash
pip install owl-notify
```

## Supported Platforms

- **Bark**: iOS notification service
- **Weixin (Text)**: Weixin Work Bot with plain text format
- **Weixin (Markdown V2)**: Weixin Work Bot with markdown formatting support
- **Custom Webhooks**: Any HTTP-based webhook service (Slack, Discord, Feishu, etc.)

## Naming Convention

**New in v0.2.0**: Unified naming convention for all platforms:

- **Platform and channel** are separated by dot (`.`)
- **Platform names** use underscores (`_`) for word separation
- **Channel names** use hyphens (`-`) for word separation
- Example: `weixin_markdown_v2.nbl-alerts`

```
Platform Structure:
platform.channel-name

Examples:
- bark.phone-1
- weixin.team-alerts
- weixin_markdown_v2.nbl-alerts
- webhook.slack-team1
```

## Configuration

Create a config file at `~/.owl-notify.toml` (get path via `owl --show-config`):

```toml
# Base platforms
[bark]
server_url = "https://api.day.app"
token = "your-bark-token"

[weixin]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"

[weixin_markdown_v2]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"

# Channels (inherit from base platforms)
[bark.phone-1]
token = "phone1-token"
# Inherits server_url from [bark]

[weixin.team-alerts]
key = "team-alerts-key"
# Auto-generates bot_url

[weixin_markdown_v2.nbl-alerts]
key = "nbl-alerts-key"

# Webhook channels (independent, no inheritance)
[webhook.slack-team1]
url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
method = "POST"
body = '{"text": "{{title}}\\n{{message}}"}'
```

## CLI Usage

```bash
# Send via Bark (default)
owl "Title" "Message"

# Send via specific platform
owl "Title" "Message" --platform bark
owl "Title" "Message" --platform weixin
owl "Title" "Message" --platform weixin_markdown_v2

# Send via channel
owl "Title" "Message" --platform bark.phone-1
owl "Title" "Message" --platform weixin.team-alerts
owl "Title" "Message" --platform weixin_markdown_v2.nbl-alerts

# Send via webhook
owl "Title" "Message" --platform webhook.slack-team1

# Use extra fields for webhook templates
owl "Title" "Message" --platform webhook.discord-alerts --extra from="Bot" --extra priority="high"

# Short form
owl "Title" "Message" -p webhook.slack-team1 -e from="Alert System"

# Use custom config file
owl "Title" "Message" --config /path/to/config.toml

# Show config file path
owl --show-config

# List all available platforms and channels
owl --list-platforms
```

## Python API

### Simple Usage (Recommended)

```python
import owl_notify

# Use default config (~/.owl-notify.toml)
owl_notify.send("Title", "Message")

# Method 1: Using platform constants (recommended - type-safe, autocomplete)
owl_notify.send("Title", "Message", platform=owl_notify.platform.bark)
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin)
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin_markdown_v2)

# Using channels
owl_notify.send("Title", "Message", platform=owl_notify.platform.bark.channel("phone-1"))
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin.channel("team-alerts"))
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin_markdown_v2.channel("nbl-alerts"))

# Using webhook channels
owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook.channel("slack-team1"))

# Method 2: Using strings (also supported)
owl_notify.send("Title", "Message", platform="bark")
owl_notify.send("Title", "Message", platform="bark.phone-1")
owl_notify.send("Title", "Message", platform="weixin.team-alerts")
owl_notify.send("Title", "Message", platform="webhook.slack-team1")

# Use custom config file
owl_notify.send("Title", "Message", config_path="/path/to/config.toml")

# Use extra fields for webhook templates
owl_notify.send(
    "Title",
    "Message",
    platform=owl_notify.platform.webhook.channel("discord-alerts"),
    extra={"from": "Bot", "priority": "high"}
)
```

### Class-based Usage

```python
from owl_notify import Notify, platform

# Initialize
notifier = Notify()  # Uses ~/.owl-notify.toml
notifier = Notify(config_path="/path/to/config.toml")  # Custom config

# Send notifications
notifier.send("Title", "Message", platform=platform.bark)
notifier.send("Title", "Message", platform=platform.bark.channel("phone-1"))
notifier.send("Title", "Message", platform=platform.weixin.channel("team-alerts"))
notifier.send("Title", "Message", platform=platform.webhook.channel("slack-team1"))

# List available platforms and channels
platforms = notifier.list_platforms()
# Returns: {"builtin": [...], "channels": [...]}
```

## Platform Channels

### Inheritance (bark, weixin, weixin_markdown_v2)

Channels inherit configuration from their base platform:

```toml
# Base platform
[bark]
server_url = "https://api.day.app"
token = "default-token"

# Channels inherit server_url, only override token
[bark.phone-1]
token = "phone1-token"

[bark.phone-2]
token = "phone2-token"
```

### Weixin Key Auto-Concatenation

For Weixin platforms, use the `key` field for convenience:

```toml
[weixin.team-alerts]
key = "your-webhook-key"
# Auto-generates: bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-webhook-key"
```

### Webhook Channels (Independent)

Webhook channels are independent and do not support inheritance:

```toml
# Each webhook channel must have complete configuration
[webhook.slack-team1]
url = "https://hooks.slack.com/services/T11111111/B11111111/YYYYYYYYYYYYYYYYYYYY"
method = "POST"
body = '{"text": "{{title}}\\n{{message}}"}'

[webhook.slack-team2]
url = "https://hooks.slack.com/services/T22222222/B22222222/ZZZZZZZZZZZZZZZZZZZZ"
method = "POST"
body = '{"text": "{{title}}\\n{{message}}"}'
```

### Custom Platforms (For Reusable Configurations)

If you need to reuse webhook configurations, create a custom platform:

```toml
# Custom platform
[slack]
method = "POST"
body = '{"text": "{{title}}\\n{{message}}"}'

# Channels inherit method and body
[slack.team1]
url = "https://hooks.slack.com/services/T11111111/B11111111/YYYYYYYYYYYYYYYYYYYY"

[slack.team2]
url = "https://hooks.slack.com/services/T22222222/B22222222/ZZZZZZZZZZZZZZZZZZZZ"
```

## Custom Webhook Configuration

### Template Placeholders

Use `{{placeholder}}` syntax in URLs and body templates:
- `{{title}}` - Notification title
- `{{message}}` - Notification message
- `{{key}}` - Any extra field passed via `--extra key=value`

### Common Platform Examples

#### Slack

```toml
[webhook.slack-team1]
url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
method = "POST"
body = '{"text": "{{title}}\\n\\n{{message}}"}'
```

#### Discord

```toml
[webhook.discord-alerts]
url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
method = "POST"
body = '{"content": "**{{title}}**\\n{{message}}", "username": "{{from}}"}'
```

Usage:
```bash
owl "Alert" "Something happened" -p webhook.discord-alerts -e from="Monitor"
```

#### Feishu (飞书)

```toml
[webhook.feishu-team1]
url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
method = "POST"
body = '{"msg_type": "text", "content": {"text": "{{title}}\\n{{message}}\\nFrom: {{from}}"}}'
```

#### Custom GET Request

```toml
[webhook.custom-api]
url = "https://api.example.com/notify?title={{title}}&message={{message}}&priority={{priority}}"
method = "GET"
```

## Global Defaults

Set global defaults for all platforms:

```toml
[defaults]
timeout = 30        # Request timeout in seconds
```

## Error Handling and Retry

**New in v0.2.0**: Configure automatic retry and error notifications:

```toml
[error]
max_retries = 3                                    # Maximum retry attempts (default: 3)
retry_delay_ms = 1000                              # Delay between retries in milliseconds (default: 1000ms = 1s)
notification_platform = "weixin_markdown_v2.nbl-alerts"  # Platform for error notifications
```

### How It Works

1. **Automatic Retry**: When a notification fails, it automatically retries up to `max_retries` times
2. **Retry Delay**: Waits `retry_delay_ms` milliseconds between each retry attempt
3. **Error Notification**: If all retries fail, sends an error notification to `notification_platform`
4. **No Infinite Loop**: Error notifications themselves do not retry (to prevent infinite loops)

### Example Error Notification

When a notification fails after all retries, you'll receive:

```
🚨 Notification Failed: Original Title

**Failed to send notification**

**Original Platform:** bark.phone-1
**Original Title:** Original Title
**Original Message:**
Original message content

**Time:** 2026-04-12 15:30:45
```

### Configuration Examples

```toml
# Send error notifications to Weixin Markdown
[error]
max_retries = 3
retry_delay_ms = 1000
notification_platform = "weixin_markdown_v2.nbl-alerts"

# Send error notifications to Bark with longer retry delay
[error]
max_retries = 5
retry_delay_ms = 2000  # 2 seconds
notification_platform = "bark.phone-1"

# Fast retry for critical notifications
[error]
max_retries = 10
retry_delay_ms = 500  # 0.5 seconds
notification_platform = "weixin_markdown_v2.nbl-alerts"

# Disable error notifications (only retry)
[error]
max_retries = 3
retry_delay_ms = 1000
# notification_platform = ""  # Leave empty or omit
```

See [.owl-notify.toml.example](./.owl-notify.toml.example) for a complete configuration example.

## License

Apache License 2.0
