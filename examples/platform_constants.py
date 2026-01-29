"""Example demonstrating platform constants usage."""

import owl_notify

# Method 1: Using platform constants (recommended - type-safe, IDE autocomplete)
owl_notify.send("Title", "Message", platform=owl_notify.platform.bark)
owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin)
owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook("slack"))

# Method 2: Using strings (still supported for backward compatibility)
owl_notify.send("Title", "Message", platform="bark")
owl_notify.send("Title", "Message", platform="weixin")
owl_notify.send("Title", "Message", platform="webhook.slack")

# Using Notify class with platform constants
notifier = owl_notify.Notify()
notifier.send("Title", "Message", platform=owl_notify.platform.bark)

# Custom webhook example
notifier.send(
    "Deploy Success",
    "Application deployed to production",
    platform=owl_notify.platform.webhook("discord"),
    extra={"env": "production", "version": "1.0.0"}
)
