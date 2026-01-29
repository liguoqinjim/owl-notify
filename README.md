# owl-notify

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

## Configuration

Create a config file at `~/.owl-notify.toml`:

```toml
[bark]
server_url = "https://api.day.app"
token = "your-bark-token"

[weixin]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"

[weixin_markdown_v2]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"

# Custom webhook example
[webhook.slack]
url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
method = "POST"
body = '''
{
  "text": "{{title}}\n\n{{message}}"
}
'''
```

## CLI Usage

```bash
# Send via Bark (default)
owl "Title" "Message"

# Send via Weixin (text format)
owl "Title" "Message" --platform weixin

# Send via Weixin (markdown_v2 format)
owl "Title" "Message" --platform weixin_markdown_v2

# Send via custom webhook
owl "Title" "Message" --platform webhook.slack

# Use extra fields for webhook templates
owl "Title" "Message" --platform webhook.discord --extra from="Bot" --extra priority="high"

# Short form
owl "Title" "Message" -p webhook.slack -e from="Alert System"

# Use custom config file
owl "Title" "Message" --config /path/to/config.toml

# Show config file path
owl --show-config
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
owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook("slack"))

# Method 2: Using strings (still supported for backward compatibility)
owl_notify.send("Title", "Message", platform="bark")
owl_notify.send("Title", "Message", platform="weixin")
owl_notify.send("Title", "Message", platform="weixin_markdown_v2")
owl_notify.send("Title", "Message", platform="webhook.slack")

# Use custom config file
owl_notify.send("Title", "Message", config_path="/path/to/config.toml")

# Use extra fields for webhook templates
owl_notify.send(
    "Title",
    "Message",
    platform=owl_notify.platform.webhook("discord"),
    extra={"from": "Bot", "priority": "high"}
)

# All parameters together
owl_notify.send(
    "Title",
    "Message",
    platform=owl_notify.platform.webhook("slack"),
    extra={"from": "System"},
    config_path="/custom/config.toml"
)
```

### Class-based Usage (Also Available)

```python
from owl_notify import Notify, platform

# Use default config (~/.owl-notify.toml)
notifier = Notify()

# Or specify config path
notifier = Notify(config_path="/path/to/config.toml")

# Send notification with platform constants
notifier.send("Title", "Message", platform=platform.bark)
notifier.send("Title", "Message", platform=platform.weixin)
notifier.send("Title", "Message", platform=platform.webhook("slack"))

# Or use strings (backward compatible)
notifier.send("Title", "Message", platform="bark")
notifier.send("Title", "Message", platform="weixin")

# Use extra fields
notifier.send(
    "Title",
    "Message",
    platform=platform.webhook("discord"),
    extra={"from": "Bot", "priority": "high"}
)
```

## Custom Webhook Configuration

You can define custom webhook integrations in your config file. Each webhook instance has a unique name.

### Configuration Format

```toml
[webhook.instance_name]
url = "https://api.example.com/webhook"  # Required
method = "GET"  # Optional, defaults to POST
body = '''{ "key": "{{template}}" }'''  # For POST requests
```

### Template Placeholders

Use `{{placeholder}}` syntax in URLs and body templates:
- `{{title}}` - Notification title
- `{{message}}` - Notification message
- `{{key}}` - Any extra field passed via `--extra key=value`

### Common Platform Examples

#### Slack

```toml
[webhook.slack]
url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
method = "POST"
body = '''
{
  "text": "{{title}}\n\n{{message}}"
}
'''
```

#### Discord

```toml
[webhook.discord]
url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
method = "POST"
body = '''
{
  "content": "**{{title}}**\n{{message}}",
  "username": "{{from}}"
}
'''
```

Usage with extra fields:
```bash
owl "Alert" "Something happened" -p webhook.discord -e from="Monitor"
```

#### Feishu (飞书)

```toml
[webhook.feishu]
url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
method = "POST"
body = '''
{
  "msg_type": "text",
  "content": {
    "text": "{{title}}\n{{message}}\nFrom: {{from}}"
  }
}
'''
```

#### Custom GET Request

```toml
[webhook.custom_api]
url = "https://api.example.com/notify?title={{title}}&message={{message}}&priority={{priority}}"
method = "GET"
```

Usage:
```bash
owl "Alert" "Message" -p webhook.custom_api -e priority="high"
```

## License

Apache License 2.0
