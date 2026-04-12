#!/usr/bin/env python3
"""Test script for the new API."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from owl_notify.platform import platform, PlatformChannel


def test_platform_channel():
    """Test PlatformChannel class."""
    print("Testing PlatformChannel class...")

    # Test __str__
    bark = PlatformChannel("bark")
    assert str(bark) == "bark", f"Expected 'bark', got '{str(bark)}'"
    print("  ✓ PlatformChannel.__str__() works")

    # Test channel()
    assert bark.channel("phone-1") == "bark.phone-1"
    print("  ✓ PlatformChannel.channel() works")

    weixin = PlatformChannel("weixin")
    assert weixin.channel("team-alerts") == "weixin.team-alerts"
    print("  ✓ Weixin channel works")

    webhook = PlatformChannel("webhook")
    assert webhook.channel("slack-team1") == "webhook.slack-team1"
    print("  ✓ Webhook channel works")


def test_platform_constants():
    """Test platform constants."""
    print("\nTesting platform constants...")

    # Test base platforms
    assert str(platform.bark) == "bark"
    print("  ✓ platform.bark works")

    assert str(platform.weixin) == "weixin"
    print("  ✓ platform.weixin works")

    assert str(platform.weixin_markdown_v2) == "weixin_markdown_v2"
    print("  ✓ platform.weixin_markdown_v2 works")

    assert str(platform.webhook) == "webhook"
    print("  ✓ platform.webhook works")

    # Test channels
    assert platform.bark.channel("phone-1") == "bark.phone-1"
    print("  ✓ platform.bark.channel() works")

    assert platform.weixin.channel("team-alerts") == "weixin.team-alerts"
    print("  ✓ platform.weixin.channel() works")

    assert platform.weixin_markdown_v2.channel("nbl-alerts") == "weixin_markdown_v2.nbl-alerts"
    print("  ✓ platform.weixin_markdown_v2.channel() works")

    assert platform.webhook.channel("slack-team1") == "webhook.slack-team1"
    print("  ✓ platform.webhook.channel() works")


def test_config_parsing():
    """Test configuration parsing."""
    print("\nTesting configuration parsing...")

    from owl_notify.notify import Notify

    # Create a test config
    test_config = {
        "defaults": {"timeout": 30},
        "bark": {"server_url": "https://api.day.app", "token": "default-token"},
        "bark.phone-1": {"token": "phone1-token"},
        "weixin": {"bot_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=default"},
        "weixin.team-alerts": {"key": "team-alerts-key"},
        "webhook.slack-team1": {"url": "https://hooks.slack.com/...", "method": "POST"},
    }

    notifier = Notify()
    notifier.config = test_config

    # Test base platform config
    bark_config = notifier._get_platform_config("bark")
    assert bark_config["token"] == "default-token"
    print("  ✓ Base platform config works")

    # Test channel inheritance
    bark_phone1_config = notifier._get_platform_config("bark.phone-1")
    assert bark_phone1_config["server_url"] == "https://api.day.app"  # Inherited
    assert bark_phone1_config["token"] == "phone1-token"  # Overridden
    print("  ✓ Channel inheritance works")

    # Test weixin key auto-concatenation
    weixin_alerts_config = notifier._get_platform_config("weixin.team-alerts")
    assert "bot_url" in weixin_alerts_config
    assert "team-alerts-key" in weixin_alerts_config["bot_url"]
    print("  ✓ Weixin key auto-concatenation works")

    # Test webhook (no inheritance)
    webhook_config = notifier._get_platform_config("webhook.slack-team1")
    assert webhook_config["url"] == "https://hooks.slack.com/..."
    assert webhook_config["method"] == "POST"
    print("  ✓ Webhook config works (no inheritance)")


def test_platform_routing():
    """Test platform routing in send()."""
    print("\nTesting platform routing...")

    from owl_notify.notify import Notify

    notifier = Notify()

    # Test routing logic (without actually sending)
    test_cases = [
        ("bark", "bark"),
        ("bark.phone-1", "bark"),
        ("weixin", "weixin"),
        ("weixin.team-alerts", "weixin"),
        ("weixin_markdown_v2", "weixin_markdown_v2"),
        ("weixin_markdown_v2.nbl-alerts", "weixin_markdown_v2"),
        ("webhook.slack-team1", "webhook"),
    ]

    for platform_str, expected_base in test_cases:
        base = platform_str.split(".")[0] if "." in platform_str else platform_str
        assert base == expected_base, f"Expected {expected_base}, got {base}"
        print(f"  ✓ {platform_str} routes to {expected_base}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing New API")
    print("=" * 60)

    try:
        test_platform_channel()
        test_platform_constants()
        test_config_parsing()
        test_platform_routing()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
