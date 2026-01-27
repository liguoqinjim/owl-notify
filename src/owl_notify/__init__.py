"""owl-notify: A simple notification CLI for Bark and Weixin."""

from pathlib import Path

from owl_notify.notify import Notify

__version__ = "0.1.1"
__all__ = ["Notify", "send", "__version__"]


def send(
    title: str,
    message: str,
    platform: str = "bark",
    extra: dict | None = None,
    config_path: str | Path | None = None
) -> bool:
    """Convenient module-level send function.

    Args:
        title: Notification title
        message: Notification message
        platform: Target platform (default: bark). Use 'webhook.xxx' for custom webhooks
        extra: Extra fields for webhook templates (optional)
        config_path: Path to config file (default: ~/.owl-notify.toml)

    Returns:
        True if successful, False otherwise

    Examples:
        >>> import owl_notify
        >>> owl_notify.send("Title", "Message")
        >>> owl_notify.send("Title", "Message", platform="weixin")
        >>> owl_notify.send("Title", "Message", platform="webhook.slack")
        >>> owl_notify.send("Title", "Message", config_path="/custom/config.toml")
        >>> owl_notify.send("Title", "Message", platform="webhook.discord", extra={"from": "Bot"})
    """
    notifier = Notify(config_path=config_path)
    return notifier.send(title, message, platform=platform, extra=extra)
