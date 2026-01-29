"""Notification backends for Bark and Weixin."""

from __future__ import annotations

from pathlib import Path

import requests
import toml


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
        """Get configuration for a platform with inheritance support.

        Supports instance inheritance (e.g., weixin_team1 inherits from weixin).
        Priority: instance config > base platform config > defaults

        Args:
            platform: Platform name (e.g., 'bark', 'weixin_team1', 'bark_phone1')

        Returns:
            Merged configuration dictionary
        """
        config = {}

        # Start with global defaults if present
        defaults = self.config.get("defaults", {})
        config.update(defaults)

        # Detect base platform for inheritance
        base_platform = None
        if "_" in platform:
            # Check if it's an instance (e.g., weixin_team1, bark_phone1)
            # Try to find base platform by removing suffix
            potential_bases = ["weixin_markdown_v2", "weixin", "bark"]
            for base in potential_bases:
                if platform.startswith(base + "_"):
                    base_platform = base
                    break

        # Merge base platform config
        if base_platform:
            base_config = self.config.get(base_platform, {})
            config.update(base_config)

        # Merge instance config (highest priority)
        instance_config = self.config.get(platform, {})
        config.update(instance_config)

        # Handle weixin key auto-concatenation
        if platform.startswith("weixin") and "key" in instance_config and "bot_url" not in instance_config:
            key = instance_config["key"]
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
        max_retries = config.get("max_retries", 3)

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
                else:
                    print(f"Error: Request failed after {max_retries} attempts: {e}")

        return None

    def send(self, title: str, message: str, platform: str = "bark", extra: dict | None = None) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message body
            platform: Target platform ('bark', 'weixin', 'weixin_markdown_v2', or 'webhook.xxx')
                     Supports platform instances (e.g., 'weixin_team1', 'bark_phone1')
            extra: Extra fields for custom webhook templates (optional)

        Returns:
            True if successful, False otherwise
        """
        if extra is None:
            extra = {}

        # Route to appropriate handler
        # Check longer prefixes first to avoid conflicts
        if platform.startswith("weixin_markdown_v2"):
            return self._send_weixin_markdown_v2(title, message, platform)
        elif platform.startswith("weixin"):
            return self._send_weixin(title, message, platform)
        elif platform.startswith("bark"):
            return self._send_bark(title, message, platform)
        elif platform.startswith("webhook."):
            return self._send_webhook(title, message, platform, extra)
        else:
            print(f"Error: Unknown platform: {platform}")
            return False

    def _send_bark(self, title: str, message: str, platform: str = "bark") -> bool:
        """Send notification via Bark.

        Bark API: GET/POST {server_url}/{token}/{title}/{message}

        Args:
            title: Notification title
            message: Notification message body
            platform: Platform name (supports instances like 'bark_phone1')
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
            platform: Platform name (supports instances like 'weixin_team1')
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
            platform: Platform name (supports instances like 'weixin_markdown_v2_team1')
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

        Args:
            title: Notification title
            message: Notification message body
            platform: Platform name (format: 'webhook.xxx')
            extra: Extra fields for template substitution

        Returns:
            True if successful, False otherwise
        """
        # Extract webhook instance name (e.g., 'webhook.slack' -> 'slack')
        webhook_name = platform.split(".", 1)[1] if "." in platform else ""

        # TOML creates nested dict: [webhook.slack] becomes config['webhook']['slack']
        webhook_configs = self.config.get("webhook", {})
        config = webhook_configs.get(webhook_name, {})

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
        """List all available platforms from configuration.

        Returns:
            Dictionary with keys:
            - 'builtin': Built-in platform types
            - 'instances': Platform instances from config
            - 'webhooks': Webhook platforms
        """
        builtin = ["bark", "weixin", "weixin_markdown_v2"]
        instances = []
        webhooks = []

        # Scan config for platform instances and webhooks
        for key in self.config.keys():
            if key == "defaults":
                continue

            # Skip builtin platforms
            if key in builtin:
                continue

            # Check for webhook platforms
            if key == "webhook":
                webhook_configs = self.config.get("webhook", {})
                for webhook_name in webhook_configs.keys():
                    webhooks.append(f"webhook.{webhook_name}")
                continue

            # Check if it's a platform instance
            is_instance = False
            for base in ["weixin_markdown_v2", "weixin", "bark"]:
                if key.startswith(base + "_"):
                    instances.append(key)
                    is_instance = True
                    break

            # If not an instance and not a builtin, it might be a custom base platform
            # For now, we'll skip these as they're covered by the builtin list

        return {
            "builtin": builtin,
            "instances": sorted(instances),
            "webhooks": sorted(webhooks)
        }
