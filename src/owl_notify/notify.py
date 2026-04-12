"""Notification backends for Bark and Weixin."""

from __future__ import annotations

import re
from pathlib import Path

import requests
import toml
import time


class Notify:
    """Send notifications to Bark or Weixin platforms."""

    def __init__(self, config_path: str | Path | None = None):
        """Initialize with optional config file path.

        Args:
            config_path: Path to TOML config file. Defaults to ~/.owl-notify.toml
        """
        if config_path is None:
            config_path = Path.home() / ".owl-notify.toml"
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from TOML file."""
        if not self.config_path.exists():
            print(f"Warning: Config file not found: {self.config_path}")
            return {}
        try:
            return toml.load(self.config_path)
        except Exception as e:
            print(f"Error: Failed to load config: {e}")
            return {}

    def _get_platform_config(self, platform: str) -> dict:
        """Get configuration for a platform or channel.

        TOML dotted tables like [weixin_markdown_v2.nbl] are parsed as nested dicts:
        config['weixin_markdown_v2']['nbl'].

        Args:
            platform: Platform or channel name

        Returns:
            Merged configuration dictionary
        """
        config = {}

        defaults = self.config.get("defaults", {})
        config.update(defaults)

        if "." in platform:
            base_platform, channel = platform.split(".", 1)
        else:
            base_platform = platform
            channel = None

        base_table = self.config.get(base_platform, {})
        if not isinstance(base_table, dict):
            base_table = {}

        base_config = {k: v for k, v in base_table.items() if not isinstance(v, dict)}

        if base_platform == "webhook":
            if channel:
                instance_table = base_table.get(channel, {})
                if isinstance(instance_table, dict):
                    config.update({k: v for k, v in instance_table.items() if not isinstance(v, dict)})
        else:
            config.update(base_config)
            if channel:
                instance_table = base_table.get(channel, {})
                if isinstance(instance_table, dict):
                    config.update({k: v for k, v in instance_table.items() if not isinstance(v, dict)})

        if base_platform.startswith("weixin") and "key" in config and "bot_url" not in config:
            key = config["key"]
            config["bot_url"] = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"

        return config

    def _make_request(self, method: str, url: str, platform: str, **kwargs) -> requests.Response | None:
        """Make HTTP request with retry logic and timeout.

        Args:
            method: HTTP method ('GET' or 'POST')
            url: Request URL
            platform: Platform name (for config lookup)
            **kwargs: Additional arguments for requests (json, data, headers, etc.)

        Returns:
            Response object if successful, None otherwise
        """
        config = self._get_platform_config(platform)
        timeout = config.get("timeout", 30)

        # Get retry settings from [error] section or use defaults
        error_config = self.config.get("error", {})
        max_retries = error_config.get("max_retries", 3)
        retry_delay_ms = error_config.get("retry_delay_ms", 1000)  # Default 1000ms (1 second)
        retry_delay = retry_delay_ms / 1000  # Convert to seconds for time.sleep()

        # Set timeout in kwargs if not already set
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                if method.upper() == "GET":
                    resp = requests.get(url, **kwargs)
                elif method.upper() == "POST":
                    resp = requests.post(url, **kwargs)
                else:
                    print(f"Error: Unsupported HTTP method: {method}")
                    return None

                resp.raise_for_status()
                return resp

            except requests.RequestException as e:
                last_error = e
                if attempt < max_retries:
                    print(f"Warning: Request failed (attempt {attempt}/{max_retries}): {e}")
                    print(f"Retrying in {retry_delay_ms}ms...")
                    time.sleep(retry_delay)
                else:
                    print(f"Error: Request failed after {max_retries} attempts: {e}")

        return None

    def send(self, title: str, message: str, platform: str = "bark", extra: dict | None = None, _is_error_notification: bool = False) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message body
            platform: Target platform or channel
                     Examples: 'bark', 'bark.phone-1', 'weixin.team-alerts',
                              'weixin_markdown_v2.nbl-alerts', 'webhook.slack-team1'
            extra: Extra fields for custom webhook templates (optional)
            _is_error_notification: Internal flag to prevent infinite error notification loops

        Returns:
            True if successful, False otherwise
        """
        if extra is None:
            extra = {}

        # Parse base platform from platform string
        base_platform = platform.split(".")[0] if "." in platform else platform

        # Route to appropriate handler
        # Check longer prefixes first to avoid conflicts
        result = False
        try:
            if base_platform == "weixin_markdown_v2":
                result = self._send_weixin_markdown_v2(title, message, platform)
            elif base_platform == "weixin":
                result = self._send_weixin(title, message, platform)
            elif base_platform == "bark":
                result = self._send_bark(title, message, platform)
            elif base_platform == "webhook":
                result = self._send_webhook(title, message, platform, extra)
            else:
                print(f"Error: Unknown platform: {platform}")
                result = False
        except Exception as e:
            print(f"Error: Exception during send: {e}")
            result = False

        # Send error notification if send failed and this is not already an error notification
        if not result and not _is_error_notification:
            self._send_error_notification(title, message, platform, extra)

        return result

    def _send_error_notification(self, original_title: str, original_message: str, failed_platform: str, extra: dict) -> None:
        """Send error notification when a send operation fails.

        Args:
            original_title: Title of the failed notification
            original_message: Message of the failed notification
            failed_platform: Platform that failed to send
            extra: Extra fields from the original send
        """
        # Get error notification config
        error_config = self.config.get("error", {})
        notification_platform = error_config.get("notification_platform")

        # If no error notification platform configured, skip
        if not notification_platform:
            return

        # Prepare error notification content
        error_title = f"🚨 Notification Failed: {original_title}"
        error_message = f"""**Failed to send notification**

**Original Platform:** {failed_platform}
**Original Title:** {original_title}
**Original Message:**
{original_message}

**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Send error notification (with _is_error_notification=True to prevent infinite loop)
        print(f"Sending error notification to: {notification_platform}")
        try:
            self.send(
                error_title,
                error_message,
                platform=notification_platform,
                extra=extra,
                _is_error_notification=True
            )
        except Exception as e:
            # If error notification fails, just log it (don't retry)
            print(f"Warning: Failed to send error notification: {e}")

    def _send_bark(self, title: str, message: str, platform: str = "bark") -> bool:
        """Send notification via Bark.

        Bark API: GET/POST {server_url}/{token}/{title}/{message}

        Args:
            title: Notification title
            message: Notification message body
            platform: Platform or channel name (e.g., 'bark', 'bark.phone-1')
        """
        config = self._get_platform_config(platform)
        server_url = config.get("server_url", "").rstrip("/")
        token = config.get("token", "")

        if not server_url or not token:
            print(f"Error: Bark config missing: server_url or token not set for {platform}")
            return False

        url = f"{server_url}/{token}/{title}/{message}"
        resp = self._make_request("GET", url, platform)

        if resp:
            print(f"Bark notification sent: {title}")
            return True
        return False

    def _send_weixin(self, title: str, message: str, platform: str = "weixin") -> bool:
        """Send notification via Weixin Work Bot.

        Weixin API: POST bot_url with JSON body

        Args:
            title: Notification title
            message: Notification message body
            platform: Platform or channel name (e.g., 'weixin', 'weixin.team-alerts')
        """
        config = self._get_platform_config(platform)
        bot_url = config.get("bot_url", "")

        if not bot_url:
            print(f"Error: Weixin config missing: bot_url not set for {platform}")
            return False

        payload = {
            "msgtype": "text",
            "text": {
                "content": f"{title}\n\n{message}"
            }
        }

        resp = self._make_request("POST", bot_url, platform, json=payload)

        if resp:
            data = resp.json()
            if data.get("errcode") == 0:
                print(f"Weixin notification sent: {title}")
                return True
            else:
                print(f"Error: Weixin API error: {data}")
                return False
        return False

    def _send_weixin_markdown_v2(self, title: str, message: str, platform: str = "weixin_markdown_v2") -> bool:
        """Send notification via Weixin Work Bot using markdown_v2 format.

        Weixin API: POST bot_url with markdown_v2 body

        Args:
            title: Notification title
            message: Notification message body
            platform: Platform or channel name (e.g., 'weixin_markdown_v2', 'weixin_markdown_v2.nbl-alerts')
        """
        config = self._get_platform_config(platform)
        bot_url = config.get("bot_url", "")

        if not bot_url:
            print(f"Error: Weixin markdown_v2 config missing: bot_url not set for {platform}")
            return False

        # Format content as markdown
        # If title is provided, use it as a header
        if title:
            content = f"**{title}**\n\n{message}"
        else:
            content = message

        payload = {
            "msgtype": "markdown_v2",
            "markdown_v2": {
                "content": content
            }
        }

        resp = self._make_request(
            "POST",
            bot_url,
            platform,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if resp:
            data = resp.json()
            if data.get("errcode") == 0:
                print(f"Weixin markdown_v2 notification sent: {title}")
                return True
            else:
                print(f"Error: Weixin markdown_v2 API error: {data}")
                return False
        return False

    def _send_webhook(self, title: str, message: str, platform: str, extra: dict) -> bool:
        """Send notification via custom webhook.

        Note: Webhook channels are independent and do not support inheritance.
        Each webhook.xxx channel must have its own complete configuration.

        Args:
            title: Notification title
            message: Notification message body
            platform: Webhook channel name (format: 'webhook.xxx')
            extra: Extra fields for template substitution

        Returns:
            True if successful, False otherwise
        """
        # Get config using the standard method (webhook channels are independent)
        config = self._get_platform_config(platform)

        # Get required configuration
        url = config.get("url", "")
        method = config.get("method", "POST").upper()
        body_template = config.get("body", "")

        if not url:
            print(f"Error: Webhook config missing: url not set for {platform}")
            return False

        # Prepare template variables
        template_vars = {
            "title": title,
            "message": message,
            **extra
        }

        # Replace template placeholders
        processed_url = self._replace_template(url, template_vars)

        if method == "GET":
            resp = self._make_request("GET", processed_url, platform)
        elif method == "POST":
            processed_body = self._replace_template(body_template, template_vars)
            resp = self._make_request(
                "POST",
                processed_url,
                platform,
                data=processed_body,
                headers={"Content-Type": "application/json"}
            )
        else:
            print(f"Error: Unsupported HTTP method: {method}")
            return False

        if resp:
            print(f"Webhook notification sent: {title}")
            return True
        return False

    def _replace_template(self, template: str, variables: dict) -> str:
        """Replace template placeholders with actual values.

        Args:
            template: Template string with {{key}} placeholders
            variables: Dictionary of key-value pairs to substitute

        Returns:
            String with placeholders replaced
        """
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def list_platforms(self) -> dict[str, list[str]]:
        """List available platforms and classify configured entries."""
        builtin = ["bark", "weixin", "weixin_markdown_v2", "webhook"]
        system_sections = ["defaults", "error"]
        channels = []
        invalid = []
        valid_platform_re = re.compile(r"^[a-z0-9_]+$")

        for key, value in self.config.items():
            if key in system_sections:
                continue

            if key in builtin:
                if isinstance(value, dict):
                    for child_name, child_value in value.items():
                        if isinstance(child_value, dict):
                            channels.append(f"{key}.{child_name}")
                continue

            if not isinstance(value, dict):
                invalid.append(key)
                continue

            nested_children = [child_name for child_name, child_value in value.items() if isinstance(child_value, dict)]
            if nested_children:
                if valid_platform_re.match(key):
                    channels.append(key)
                    for child_name in nested_children:
                        channels.append(f"{key}.{child_name}")
                else:
                    invalid.append(key)
                continue

            if valid_platform_re.match(key):
                channels.append(key)
            else:
                invalid.append(key)

        return {
            "builtin": builtin,
            "channels": sorted(channels),
            "invalid": sorted(invalid),
        }
