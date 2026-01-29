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
            "weixin_markdown_v2": "(Weixin Work Bot - markdown format)"
        }
        for p in platforms["builtin"]:
            desc = descriptions.get(p, "")
            print(f"  - {p:30} {desc}")

        if platforms["instances"]:
            print()
            print("Platform Instances:")
            for p in platforms["instances"]:
                # Determine base platform
                base = None
                for b in ["weixin_markdown_v2", "weixin", "bark"]:
                    if p.startswith(b + "_"):
                        base = b
                        break
                if base:
                    print(f"  - {p:30} (instance of {base})")
                else:
                    print(f"  - {p}")

        if platforms["webhooks"]:
            print()
            print("Webhook Platforms:")
            for p in platforms["webhooks"]:
                print(f"  - {p}")

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
