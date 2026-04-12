"""Platform constants for owl-notify.

Provides constants for platform selection to avoid typos and enable IDE autocomplete.
"""

from __future__ import annotations


class PlatformChannel:
    """Helper class for creating platform channel identifiers.

    This class represents a platform and provides a method to create channel identifiers.
    It can be used as a string (returns the platform name) or to create channel identifiers.
    """

    def __init__(self, platform_name: str):
        """Initialize with platform name.

        Args:
            platform_name: The base platform name (e.g., "bark", "weixin", "webhook")
        """
        self._platform_name = platform_name

    def __str__(self) -> str:
        """Return the platform name when used as a string.

        This allows the platform constant to be used directly as a platform identifier.

        Returns:
            The platform name

        Examples:
            >>> bark = PlatformChannel("bark")
            >>> str(bark)
            'bark'
        """
        return self._platform_name

    def channel(self, name: str) -> str:
        """Create a channel identifier for this platform.

        Args:
            name: Channel name (e.g., "phone-1", "team-alerts", "slack-team1")
                 Channel names should use hyphens (-) for word separation.

        Returns:
            A channel identifier in the format "{platform}.{name}"

        Examples:
            >>> bark = PlatformChannel("bark")
            >>> bark.channel("phone-1")
            'bark.phone-1'
            >>> weixin = PlatformChannel("weixin")
            >>> weixin.channel("team-alerts")
            'weixin.team-alerts'
            >>> webhook = PlatformChannel("webhook")
            >>> webhook.channel("slack-team1")
            'webhook.slack-team1'
        """
        return f"{self._platform_name}.{name}"


class platform:
    """Platform constants and helpers for notification backends.

    All platforms follow the same pattern:
    - Use the platform constant directly for the default channel
    - Use platform.channel("name") to specify a custom channel

    Naming conventions:
    - Platform names use underscores (_) for word separation
    - Channel names use hyphens (-) for word separation
    - Platform and channel are separated by a dot (.)

    Examples:
        Basic platforms:
        >>> import owl_notify
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.bark)
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin)
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook)

        Platform channels:
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.bark.channel("phone-1"))
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.weixin.channel("team-alerts"))
        >>> owl_notify.send("Title", "Message", platform=owl_notify.platform.webhook.channel("slack-team1"))

        Using strings (also supported):
        >>> owl_notify.send("Title", "Message", platform="bark")
        >>> owl_notify.send("Title", "Message", platform="bark.phone-1")
        >>> owl_notify.send("Title", "Message", platform="webhook.slack-team1")
    """

    bark: PlatformChannel = PlatformChannel("bark")
    """Bark notification platform.

    Examples:
        >>> platform.bark  # Default channel
        'bark'
        >>> platform.bark.channel("phone-1")  # Custom channel
        'bark.phone-1'
    """

    weixin: PlatformChannel = PlatformChannel("weixin")
    """Weixin Work Bot notification platform (text format).

    Examples:
        >>> platform.weixin  # Default channel
        'weixin'
        >>> platform.weixin.channel("team-alerts")  # Custom channel
        'weixin.team-alerts'
    """

    weixin_markdown_v2: PlatformChannel = PlatformChannel("weixin_markdown_v2")
    """Weixin Work Bot notification platform (markdown_v2 format).

    Examples:
        >>> platform.weixin_markdown_v2  # Default channel
        'weixin_markdown_v2'
        >>> platform.weixin_markdown_v2.channel("nbl-alerts")  # Custom channel
        'weixin_markdown_v2.nbl-alerts'
    """

    webhook: PlatformChannel = PlatformChannel("webhook")
    """Custom webhook notification platform.

    Note: Webhook channels are independent and do not support inheritance.
    Each webhook.xxx channel must have its own complete configuration.

    Examples:
        >>> platform.webhook.channel("slack-team1")  # Independent channel
        'webhook.slack-team1'
        >>> platform.webhook.channel("discord-alerts")  # Independent channel
        'webhook.discord-alerts'
    """
