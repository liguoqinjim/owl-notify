"""Example demonstrating Weixin Markdown V2 usage."""

import owl_notify

# Example 1: Simple markdown notification
def send_simple_markdown():
    """Send a simple markdown formatted notification."""
    owl_notify.send(
        "系统通知",
        "应用部署成功 ✅",
        platform=owl_notify.platform.weixin_markdown_v2
    )


# Example 2: Rich markdown content
def send_rich_markdown():
    """Send a rich markdown formatted notification with multiple elements."""
    title = "📊 每日数据报告"
    message = """
## 关键指标

- **用户数**: 1,234
- **活跃率**: 85%
- **收入**: ¥12,345

### 趋势分析
本周数据相比上周增长 **15%**

> 数据更新时间: 2024-01-20 10:00:00
"""

    owl_notify.send(
        title,
        message,
        platform=owl_notify.platform.weixin_markdown_v2
    )


# Example 3: Alert notification
def send_alert():
    """Send an alert notification with markdown formatting."""
    title = "⚠️ 系统警告"
    message = """
## 错误详情

- **类型**: Database Connection Error
- **服务**: user-service
- **环境**: Production
- **时间**: 2024-01-20 10:30:15

### 影响范围
用户登录功能受到影响

**请立即处理！**
"""

    owl_notify.send(
        title,
        message,
        platform=owl_notify.platform.weixin_markdown_v2
    )


# Example 4: Comparison - text vs markdown
def compare_text_and_markdown():
    """Compare text and markdown formats."""
    title = "部署通知"
    message = "应用 v1.2.3 已部署到生产环境"

    # Send via text format
    print("Sending via weixin (text format)...")
    owl_notify.send(title, message, platform=owl_notify.platform.weixin)

    # Send via markdown format
    print("Sending via weixin_markdown_v2 (markdown format)...")
    owl_notify.send(title, message, platform=owl_notify.platform.weixin_markdown_v2)


# Example 5: Using Notify class
def use_notify_class():
    """Demonstrate class-based usage with markdown."""
    notifier = owl_notify.Notify()

    notifier.send(
        "任务开始",
        "正在处理数据...",
        platform=owl_notify.platform.weixin_markdown_v2
    )

    # Simulate some work...
    import time
    time.sleep(1)

    notifier.send(
        "任务完成",
        """
## 处理结果

- **处理记录数**: 1,000
- **成功**: 995
- **失败**: 5
- **耗时**: 30秒

### 状态
✅ 任务执行成功
""",
        platform=owl_notify.platform.weixin_markdown_v2
    )


if __name__ == "__main__":
    print("Weixin Markdown V2 Examples")
    print("=" * 50)
    print("\nNote: Make sure you have configured weixin_markdown_v2 in ~/.owl-notify.toml")
    print("\nExample config:")
    print("[weixin_markdown_v2]")
    print('bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key"')
    print()

    # Uncomment to run examples:
    # send_simple_markdown()
    # send_rich_markdown()
    # send_alert()
    # compare_text_and_markdown()
    # use_notify_class()
