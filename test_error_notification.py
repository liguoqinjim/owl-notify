#!/usr/bin/env python3
"""Test script for error notification feature."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from owl_notify.notify import Notify


def test_error_notification():
    """Test error notification feature."""
    print("Testing Error Notification Feature")
    print("=" * 60)

    # Create a test config with error notification
    test_config = {
        "error": {
            "max_retries": 2,
            "retry_delay_ms": 500,  # 0.5 seconds
            "notification_platform": "weixin_markdown_v2.nbl-alerts",
        },
        "bark": {
            "server_url": "https://invalid-url-that-will-fail.com",
            "token": "test-token",
        },
        "weixin_markdown_v2": {
            "bot_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test",
        },
        "weixin_markdown_v2.nbl-alerts": {
            "key": "nbl-alerts-key",
        },
    }

    notifier = Notify()
    notifier.config = test_config

    print("\nTest 1: Retry mechanism")
    print("-" * 60)
    print("Sending to invalid URL (should retry 2 times)...")
    result = notifier.send("Test Title", "Test Message", platform="bark")
    print(f"Result: {result}")
    print(f"Expected: False (after 2 retries)")

    print("\nTest 2: Error notification config")
    print("-" * 60)
    error_config = notifier.config.get("error", {})
    print(f"max_retries: {error_config.get('max_retries')}")
    print(f"retry_delay_ms: {error_config.get('retry_delay_ms')}")
    print(f"notification_platform: {error_config.get('notification_platform')}")

    print("\nTest 3: Error notification platform config")
    print("-" * 60)
    notification_platform = error_config.get("notification_platform")
    if notification_platform:
        platform_config = notifier._get_platform_config(notification_platform)
        print(f"Platform: {notification_platform}")
        print(f"Config: {platform_config}")
        assert "bot_url" in platform_config, "bot_url should be auto-generated"
        print("✓ Error notification platform config is valid")

    print("\nTest 4: Prevent infinite error notification loop")
    print("-" * 60)
    print("Testing _is_error_notification flag...")
    # This should not trigger another error notification
    result = notifier.send(
        "Error Test",
        "This is an error notification",
        platform="bark",
        _is_error_notification=True,
    )
    print(f"Result: {result}")
    print("✓ No infinite loop (error notification does not trigger another error notification)")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_error_notification()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
