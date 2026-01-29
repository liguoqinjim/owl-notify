"""Complete example showing all features of owl-notify with platform constants."""

import owl_notify

# Example 1: Quick notification using constants
def notify_deployment():
    """Send deployment notification using platform constants."""
    owl_notify.send(
        "Deployment Complete",
        "Application v1.2.3 deployed successfully",
        platform=owl_notify.platform.bark
    )


# Example 2: Error notification
def notify_error(error_msg: str):
    """Send error notification to Weixin."""
    owl_notify.send(
        "⚠️ Application Error",
        f"An error occurred: {error_msg}",
        platform=owl_notify.platform.weixin
    )


# Example 3: Webhook with extra fields
def notify_slack(event: str, details: dict):
    """Send notification to Slack with custom fields."""
    owl_notify.send(
        f"Event: {event}",
        f"Details: {details}",
        platform=owl_notify.platform.webhook("slack"),
        extra={"env": "production", "severity": "high"}
    )


# Example 4: Multiple platforms for critical alerts
def critical_alert(title: str, message: str):
    """Send critical alert to multiple platforms."""
    platforms = [
        owl_notify.platform.bark,
        owl_notify.platform.weixin,
        owl_notify.platform.webhook("slack"),
    ]

    for platform in platforms:
        success = owl_notify.send(title, message, platform=platform)
        if not success:
            print(f"Failed to send to {platform}")


# Example 5: Using Notify class with constants
def advanced_usage():
    """Demonstrate class-based usage with platform constants."""
    notifier = owl_notify.Notify()

    # Send to different platforms
    notifier.send("Task Started", "Processing data...", platform=owl_notify.platform.bark)

    # Simulate some work...
    import time
    time.sleep(1)

    notifier.send("Task Complete", "Data processed successfully", platform=owl_notify.platform.bark)


# Example 6: Custom webhook helper
def create_custom_platform(service_name: str) -> str:
    """Helper function to create custom webhook platform identifier."""
    return owl_notify.platform.webhook(service_name)


if __name__ == "__main__":
    print("Example: Using platform constants")
    print("=" * 50)

    # Show available platforms
    print(f"Available platforms:")
    print(f"  - owl_notify.platform.bark")
    print(f"  - owl_notify.platform.weixin")
    print(f"  - owl_notify.platform.webhook('name')")
    print()

    # Show constant values
    print(f"Constant values:")
    print(f"  bark = {owl_notify.platform.bark!r}")
    print(f"  weixin = {owl_notify.platform.weixin!r}")
    print(f"  webhook('slack') = {owl_notify.platform.webhook('slack')!r}")
    print()

    # Example of backward compatibility
    print(f"Backward compatibility:")
    print(f"  Both methods work:")
    print(f"    platform=owl_notify.platform.bark")
    print(f"    platform='bark'")
    print(f"  Both are equivalent!")
