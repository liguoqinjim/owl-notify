"""Command-line interface for owl-notify."""

import argparse
import sys
from pathlib import Path

from owl_notify import __version__
from owl_notify.notify import Notify


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="owl",
        description="Send notifications to Bark, Weixin, or custom webhooks",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show the absolute path of the config file and exit",
    )
    parser.add_argument(
        "--list-platforms",
        "-l",
        action="store_true",
        help="List all available platforms from config file and exit",
    )
    parser.add_argument(
        "title",
        nargs="?",
        help="Notification title",
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="Notification message body",
    )
    parser.add_argument(
        "--platform",
        "-p",
        default="bark",
        help="Target platform (default: bark). Use 'webhook.xxx' for custom webhooks",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path.home() / ".owl-notify.toml",
        help="Path to config file (default: ~/.owl-notify.toml)",
    )
    parser.add_argument(
        "--extra",
        "-e",
        action="append",
        help="Extra fields for webhook templates (format: key=value). Can be used multiple times",
    )

    args = parser.parse_args()

    # Handle --show-config flag
    if args.show_config:
        config_path = args.config.resolve()
        print(f"Config file path: {config_path}")
        if config_path.exists():
            print(f"Status: File exists")
        else:
            print(f"Status: File not found")
        return 0

    # Handle --list-platforms flag
    if args.list_platforms:
        notifier = Notify(config_path=args.config)
        platforms = notifier.list_platforms()

        print("Available Platforms:")
        print("=" * 40)
        print()
        print("Built-in Platforms:")
        descriptions = {
            "bark": "(Bark notification service)",
            "weixin": "(Weixin Work Bot - text format)",
            "weixin_markdown_v2": "(Weixin Work Bot - markdown format)",
            "webhook": "(Custom webhook - independent channels)",
        }
        for p in platforms["builtin"]:
            desc = descriptions.get(p, "")
            print(f"  - {p:30} {desc}")

        if platforms["channels"]:
            print()
            print("Configured Channels:")
            grouped_channels = {}
            for p in platforms["channels"]:
                base = p.split(".", 1)[0]
                if base not in grouped_channels:
                    grouped_channels[base] = []
                grouped_channels[base].append(p)

            ordered_platforms = []
            for platform_name in platforms["builtin"]:
                if platform_name in grouped_channels:
                    ordered_platforms.append(platform_name)
            for platform_name in grouped_channels:
                if platform_name not in ordered_platforms:
                    ordered_platforms.append(platform_name)

            for platform_name in ordered_platforms:
                print(f"  - {platform_name}")
                for channel_name in grouped_channels[platform_name]:
                    print(f"    - {channel_name}")

        if platforms["invalid"]:
            print()
            print("Invalid Entries:")
            for p in platforms["invalid"]:
                print(f"  ❌ {p}")

            print()
            print("Invalid entries do not match the supported channel format: platform.channel-name")
            print("Platform names use underscores (_); channel names use hyphens (-).")
            print("Example: weixin_markdown_v2.nbl-alerts")

        print()
        print("Usage:")
        print("  owl 'Title' 'Message' --platform bark")
        print("  owl 'Title' 'Message' --platform bark.phone-1")
        print("  owl 'Title' 'Message' --platform weixin.team-alerts")
        print("  owl 'Title' 'Message' --platform webhook.slack-team1")
        return 0

        print()
        print("Usage:")
        print("  owl 'Title' 'Message' --platform bark")
        print("  owl 'Title' 'Message' --platform bark.phone-1")
        print("  owl 'Title' 'Message' --platform weixin.team-alerts")
        print("  owl 'Title' 'Message' --platform webhook.slack-team1")
        return 0

    # Validate required arguments for sending notification
    if not args.title or not args.message:
        parser.error("title and message are required when not using --show-config or --list-platforms")

    # Parse extra fields
    extra_fields = {}
    if args.extra:
        for item in args.extra:
            if "=" not in item:
                parser.error(f"Invalid extra field format: {item}. Expected key=value")
            key, value = item.split("=", 1)
            extra_fields[key.strip()] = value.strip()

    notifier = Notify(config_path=args.config)
    success = notifier.send(args.title, args.message, platform=args.platform, extra=extra_fields)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
