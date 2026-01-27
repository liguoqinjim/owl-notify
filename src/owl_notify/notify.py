"""Notification backends for Bark and Weixin."""

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

    def send(self, title: str, message: str, platform: str = "bark") -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message body
            platform: Target platform ('bark' or 'weixin')

        Returns:
            True if successful, False otherwise
        """
        if platform == "bark":
            return self._send_bark(title, message)
        elif platform == "weixin":
            return self._send_weixin(title, message)
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
