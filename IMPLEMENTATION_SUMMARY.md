# Implementation Summary: Configuration Inheritance + CLI List Platforms + Timeout/Retry

## Overview

Successfully implemented three major features for owl-notify:

1. **Configuration Inheritance** - Platform instances can inherit from base configurations
2. **CLI Platform Listing** - `--list-platforms` flag to show available platforms
3. **Timeout and Retry** - Configurable timeout and retry logic for network requests

## Features Implemented

### 1. Configuration Inheritance

#### How It Works

- **Instance Detection**: Platforms named `{base}_{instance}` automatically inherit from `{base}`
  - Example: `weixin_team1` inherits from `weixin`
  - Example: `bark_phone1` inherits from `bark`

- **Priority Order**: `instance config > base platform config > global defaults`

- **Weixin Key Auto-Concatenation**: If a weixin instance only has a `key` field, the full `bot_url` is automatically generated:
  ```toml
  [weixin_team1]
  key = "team1-key"
  # Auto-generates: bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=team1-key"
  ```

#### Example Configuration

```toml
# Global defaults (optional)
[defaults]
timeout = 30
max_retries = 3

# Base platform
[bark]
server_url = "https://api.day.app"
token = "base-token"

# Instance - inherits server_url, overrides token
[bark_phone1]
token = "phone1-token"

# Weixin with key auto-concatenation
[weixin_team1]
key = "team1-key"  # Auto-generates full bot_url
```

#### Usage

```python
import owl_notify

# Use base platform
owl_notify.send("Title", "Message", platform="bark")

# Use instance
owl_notify.send("Title", "Message", platform="bark_phone1")
owl_notify.send("Title", "Message", platform="weixin_team1")
```

### 2. CLI List Platforms

#### Command

```bash
owl --list-platforms
owl -l  # Short form
```

#### Output Example

```
Available Platforms:
========================================

Built-in Platforms:
  - bark                           (Bark notification service)
  - weixin                         (Weixin Work Bot - text format)
  - weixin_markdown_v2             (Weixin Work Bot - markdown format)

Platform Instances:
  - bark_phone1                    (instance of bark)
  - weixin_team1                   (instance of weixin)

Webhook Platforms:
  - webhook.slack
```

### 3. Timeout and Retry

#### Configuration

```toml
[defaults]
timeout = 30       # Request timeout in seconds (default: 30)
max_retries = 3    # Number of retry attempts (default: 3)

# Can be overridden per platform
[weixin]
bot_url = "..."
timeout = 60       # Custom timeout for this platform

# Can be overridden per instance
[weixin_team1]
key = "..."
max_retries = 5    # Custom retry count for this instance
```

#### Retry Behavior

- **Network Errors Only**: Retries only on connection timeouts, network failures, etc.
- **Business Errors Excluded**: Does NOT retry on API errors (e.g., Weixin `errcode != 0`)
- **Logging**:
  - During retry: `Warning: Request failed (attempt 1/3): {error}`
  - After failure: `Error: Request failed after 3 attempts: {error}`

## Code Changes

### New Methods in `notify.py`

1. **`_get_platform_config(platform: str) -> dict`**
   - Implements configuration inheritance
   - Handles key auto-concatenation for weixin platforms
   - Merges defaults → base config → instance config

2. **`_make_request(method, url, platform, **kwargs) -> Response | None`**
   - Unified network request handler
   - Implements timeout and retry logic
   - Used by all `_send_*` methods

3. **`list_platforms() -> dict[str, list[str]]`**
   - Scans config file for all available platforms
   - Returns categorized list (builtin, instances, webhooks)

### Modified Methods

1. **`send()`** - Updated routing logic to use `startswith()` for instance matching
2. **`_send_bark()`** - Added `platform` parameter, uses new helper methods
3. **`_send_weixin()`** - Added `platform` parameter, uses new helper methods
4. **`_send_weixin_markdown_v2()`** - Added `platform` parameter, uses new helper methods
5. **`_send_webhook()`** - Uses `_make_request()` for network calls

### CLI Changes in `cli.py`

- Added `--list-platforms` / `-l` argument
- Added handler to call `list_platforms()` and format output
- Updated help text for validation error

### Documentation

- Updated `.owl-notify.toml.example` with comprehensive examples showing:
  - `[defaults]` section
  - Platform instances
  - Key auto-concatenation
  - Configuration inheritance with comments

## Testing

All features tested and verified:

### ✓ Configuration Inheritance Tests
- Base platform inheritance works correctly
- Instance config overrides base config
- Global defaults apply correctly
- Key auto-concatenation works for weixin

### ✓ Timeout and Retry Tests
- Retry logic triggers on network errors
- Correct number of retries attempted
- Proper logging output
- Timeout values respected

### ✓ Backward Compatibility Tests
- Old-style configs (no defaults, no instances) still work
- Existing API calls remain unchanged
- Default values applied when not specified

### ✓ CLI Tests
- `--list-platforms` shows all platform types
- Short flag `-l` works correctly
- Platform instances correctly categorized

## Backward Compatibility

**100% backward compatible** - All existing configurations and API calls continue to work without modification:

- Old configs without `[defaults]` or instances work fine
- Existing platform names (`bark`, `weixin`, etc.) unchanged
- API signature remains the same
- All new features are opt-in enhancements

## Usage Examples

### Simple Instance Usage

```toml
# Config file
[weixin]
bot_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=base"

[weixin_alerts]
key = "alerts-key"
```

```python
# Code - just two lines as always
import owl_notify
owl_notify.send("Alert", "Something happened", platform="weixin_alerts")
```

### With Custom Timeout

```toml
[defaults]
timeout = 15
max_retries = 2

[bark_critical]
server_url = "https://api.day.app"
token = "critical-token"
timeout = 5  # Override for critical alerts
```

### List Available Platforms

```bash
$ owl -l
Available Platforms:
========================================

Built-in Platforms:
  - bark                           (Bark notification service)
  - weixin                         (Weixin Work Bot - text format)
  - weixin_markdown_v2             (Weixin Work Bot - markdown format)

Platform Instances:
  - bark_critical                  (instance of bark)
  - weixin_alerts                  (instance of weixin)
```

## Implementation Stats

- **Files Modified**: 3
  - `src/owl_notify/notify.py` (major changes)
  - `src/owl_notify/cli.py` (new flag)
  - `.owl-notify.toml.example` (documentation)

- **New Lines of Code**: ~150 lines
- **Methods Added**: 3
- **Methods Modified**: 5
- **Tests Passed**: All (inheritance, retry, backward compatibility, CLI)

## Next Steps (Optional Future Enhancements)

1. Add support for `weixin_markdown_v2_*` instances
2. Allow webhook platforms to have instances
3. Add configuration validation on load
4. Support environment variable substitution in config
5. Add exponential backoff for retries

---

**Status**: ✅ All features implemented and tested successfully
**Backward Compatibility**: ✅ 100% compatible with existing code
**Documentation**: ✅ Updated with comprehensive examples
