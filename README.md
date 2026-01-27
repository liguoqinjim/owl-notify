# owl-notify

A simple notification CLI for Bark and Weixin.

## Installation

```bash
pip install owl-notify
```

## Configuration

Create a config file at `~/.owl-notify.toml`:

```toml
[bark]
server_url = "https://api.day.app"
token = "your-bark-token"

[weixin]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"
```

## CLI Usage

```bash
# Send via Bark (default)
owl "Title" "Message"

# Send via Weixin
owl "Title" "Message" --platform weixin

# Use custom config file
owl "Title" "Message" --config /path/to/config.toml

# Show config file path
owl --show-config
```

## Python API

```python
from owl_notify import Notify

# Use default config (~/.owl-notify.toml)
notifier = Notify()

# Or specify config path
notifier = Notify(config_path="/path/to/config.toml")

# Send notification
notifier.send("Title", "Message", platform="bark")
notifier.send("Title", "Message", platform="weixin")
```

## License

Apache License 2.0
