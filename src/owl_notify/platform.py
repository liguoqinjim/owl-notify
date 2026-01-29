"""Platform constants for owl-notify.

Provides constants for platform selection to avoid typos and enable IDE autocomplete.
"""

from __future__ import annotations


class platform:
    """Platform constants and helpers for notification backends.

    Examples:
        >>> import owl_notify
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.bark)
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin)
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin_markdown_v2)
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook("slack"))
    """

    bark: str = "bark"
    """Bark notification platform."""

    weixin: str = "weixin"
    """Weixin Work Bot notification platform (text format)."""

    weixin_markdown_v2: str = "weixin_markdown_v2"
    """Weixin Work Bot notification platform (markdown_v2 format)."""

    @staticmethod
    def webhook(name: str) -> str:
        """Create a webhook platform identifier.

        Args:
            name: The webhook configuration name (e.g., "slack", "discord")

        Returns:
            A webhook platform identifier in the format "webhook.{name}"

        Examples:
            >>> platform.webhook("slack")
            'webhook.slack'
            >>> platform.webhook("discord")
            'webhook.discord'
        """
        return f"webhook.{name}"
