# Quick Start Guide

## Installation

```bash
pip install owl-notify
```

## Configuration

Create `~/.owl-notify.toml`:

```toml
[bark]
server_url = "https://api.day.app"
token = "your-bark-token"

[weixin]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"

[weixin_markdown_v2]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"
```

## Basic Usage

### CLI

```bash
# Bark (default)
owl "Hello" "World"

# Weixin (text)
owl "Hello" "World" --platform weixin

# Weixin (markdown)
owl "Report" "**Important**: Task completed ✅" --platform weixin_markdown_v2
```

### Python API

```python
import owl_notify

# Using platform constants (recommended)
owl_notify.send("Title", "Message", platform=owl_notify.platform.bark)
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin)
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin_markdown_v2)

# Or using strings
owl_notify.send("Title", "Message", platform="bark")
owl_notify.send("Title", "Message", platform="weixin_markdown_v2")
```

## Platform Comparison

### Weixin (Text) vs Weixin (Markdown V2)

**Weixin Text (`weixin`)**
- Simple plain text messages
- No formatting support
- Best for simple notifications

```python
owl_notify.send(
    "Notification",
    "Task completed successfully",
    platform=owl_notify.platform.weixin
)
```

**Weixin Markdown V2 (`weixin_markdown_v2`)**
- Rich markdown formatting
- Supports bold, lists, headers, etc.
- Best for detailed reports and alerts

```python
owl_notify.send(
    "Daily Report",
    """
## Key Metrics

- **Users**: 1,234
- **Revenue**: ¥12,345
- **Growth**: 15%

> Updated: 2024-01-20
""",
    platform=owl_notify.platform.weixin_markdown_v2
)
```

## Common Use Cases

### 1. Deployment Notification

```python
import owl_notify

owl_notify.send(
    "Deployment Complete",
    "Application v1.2.3 deployed to production ✅",
    platform=owl_notify.platform.bark
)
```

### 2. Error Alert

```python
owl_notify.send(
    "⚠️ Error Alert",
    """
## Error Details

- **Type**: Database Connection
- **Service**: user-service
- **Time**: 2024-01-20 10:30

**Action Required!**
""",
    platform=owl_notify.platform.weixin_markdown_v2
)
```

### 3. Daily Report

```python
owl_notify.send(
    "📊 Daily Report",
    """
## Summary

- **Active Users**: 1,500
- **New Signups**: 50
- **Revenue**: ¥8,888

### Trend
↗️ All metrics up compared to yesterday
""",
    platform=owl_notify.platform.weixin_markdown_v2
)
```

### 4. Custom Webhook (Slack)

```python
owl_notify.send(
    "Build Status",
    "Build #123 passed all tests",
    platform=owl_notify.platform.webhook("slack")
)
```

## Next Steps

- See [README.md](README.md) for full documentation
- Check [examples/](examples/) for more code examples
- Copy [examples/config.example.toml](examples/config.example.toml) to get started
