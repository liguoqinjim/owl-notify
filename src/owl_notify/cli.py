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
        description="Send notifications to Bark or Weixin",
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
        choices=["bark", "weixin"],
        default="bark",
        help="Target platform (default: bark)",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path.home() / ".owl-notify.toml",
        help="Path to config file (default: ~/.owl-notify.toml)",
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

    # Validate required arguments for sending notification
    if not args.title or not args.message:
        parser.error("title and message are required when not using --show-config")

    notifier = Notify(config_path=args.config)
    success = notifier.send(args.title, args.message, platform=args.platform)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
