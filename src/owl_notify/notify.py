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

    def send(self, title: str, message: str, platform: str = "bark", extra: dict | None = None) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message body
            platform: Target platform ('bark', 'weixin', 'weixin_markdown_v2', or 'webhook.xxx')
            extra: Extra fields for custom webhook templates (optional)

        Returns:
            True if successful, False otherwise
        """
        if extra is None:
            extra = {}

        if platform == "bark":
            return self._send_bark(title, message)
        elif platform == "weixin":
            return self._send_weixin(title, message)
        elif platform == "weixin_markdown_v2":
            return self._send_weixin_markdown_v2(title, message)
        elif platform.startswith("webhook."):
            return self._send_webhook(title, message, platform, extra)
        else:
            print(f"Error: Unknown platform: {platform}")
            return False

    def _send_bark(self, title: str, message: str) -> bool:
        """Send notification via Bark.

        Bark API: GET/POST {server_url}/{token}/{title}/{message}
        """
        config = self.config.get("bark", {})
        server_url = config.get("server_url", "").rstrip("/")
        token = config.get("token", "")

        if not server_url or not token:
            print("Error: Bark config missing: server_url or token not set")
            return False

        url = f"{server_url}/{token}/{title}/{message}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            print(f"Bark notification sent: {title}")
            return True
        except requests.RequestException as e:
            print(f"Error: Bark request failed: {e}")
            return False

    def _send_weixin(self, title: str, message: str) -> bool:
        """Send notification via Weixin Work Bot.

        Weixin API: POST bot_url with JSON body
        """
        config = self.config.get("weixin", {})
        bot_url = config.get("bot_url", "")

        if not bot_url:
            print("Error: Weixin config missing: bot_url not set")
            return False

        payload = {
            "msgtype": "text",
            "text": {
                "content": f"{title}\n\n{message}"
            }
        }
        try:
            resp = requests.post(bot_url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("errcode") == 0:
                print(f"Weixin notification sent: {title}")
                return True
            else:
                print(f"Error: Weixin API error: {data}")
                return False
        except requests.RequestException as e:
            print(f"Error: Weixin request failed: {e}")
            return False

    def _send_weixin_markdown_v2(self, title: str, message: str) -> bool:
        """Send notification via Weixin Work Bot using markdown_v2 format.

        Weixin API: POST bot_url with markdown_v2 body
        """
        config = self.config.get("weixin_markdown_v2", {})
        bot_url = config.get("bot_url", "")

        if not bot_url:
            print("Error: Weixin markdown_v2 config missing: bot_url not set")
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

        try:
            resp = requests.post(
                bot_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("errcode") == 0:
                print(f"Weixin markdown_v2 notification sent: {title}")
                return True
            else:
                print(f"Error: Weixin markdown_v2 API error: {data}")
                return False
        except requests.RequestException as e:
            print(f"Error: Weixin markdown_v2 request failed: {e}")
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

        try:
            if method == "GET":
                resp = requests.get(processed_url, timeout=10)
            elif method == "POST":
                processed_body = self._replace_template(body_template, template_vars)
                resp = requests.post(
                    processed_url,
                    data=processed_body,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            else:
                print(f"Error: Unsupported HTTP method: {method}")
                return False

            resp.raise_for_status()
            print(f"Webhook notification sent: {title}")
            return True
        except requests.RequestException as e:
            print(f"Error: Webhook request failed: {e}")
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
