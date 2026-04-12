# Refactoring Summary: Unified Naming Convention

## Overview

This refactoring introduces a unified naming convention for owl-notify platforms and channels, making the API more consistent, readable, and extensible.

## Changes Made

### 1. Platform API (`src/owl_notify/platform.py`)

**New `PlatformChannel` class**:
- Represents a platform with channel creation capability
- Can be used as a string (returns platform name)
- Provides `.channel(name)` method to create channel identifiers

**Updated `platform` class**:
- All platforms now use `PlatformChannel` instances
- Unified API: `platform.bark.channel("phone-1")`
- Webhook is no longer a special case

**Example**:
```python
# Base platforms
owl_notify.platform.bark                                    # "bark"
owl_notify.platform.weixin                                  # "weixin"
owl_notify.platform.webhook                                 # "webhook"

# Channels
owl_notify.platform.bark.channel("phone-1")                 # "bark.phone-1"
owl_notify.platform.weixin.channel("team-alerts")           # "weixin.team-alerts"
owl_notify.platform.webhook.channel("slack-team1")          # "webhook.slack-team1"
```

### 2. Notify Class (`src/owl_notify/notify.py`)

**Updated `_get_platform_config()`**:
- Parses platform and channel from dot-separated string
- Supports inheritance for bark, weixin, weixin_markdown_v2
- Webhook channels are independent (no inheritance)
- Maintains weixin key auto-concatenation

**Updated `send()`**:
- Routes based on base platform (before dot)
- Supports new naming convention

**Updated `list_platforms()`**:
- Returns `{"builtin": [...], "channels": [...]}`
- Simplified structure

### 3. CLI (`src/owl_notify/cli.py`)

**Updated `--list-platforms` output**:
- Shows builtin platforms and configured channels
- Indicates channel relationships
- Updated usage examples

### 4. Configuration Files

**Updated `.owl-notify.toml.example`**:
- Complete example with new naming convention
- Explains inheritance rules
- Shows webhook independence
- Includes custom platform examples

**Updated `README.md`**:
- New naming convention section
- Updated all examples
- Platform channels documentation


## Naming Convention

### Rules

1. **Platform and channel** are separated by dot (`.`)
2. **Platform names** use underscores (`_`) for word separation
3. **Channel names** use hyphens (`-`) for word separation

### Examples

```
platform.channel-name

Examples:
- bark.phone-1
- weixin.team-alerts
- weixin_markdown_v2.nbl-alerts
- webhook.slack-team1
```

### Rationale

- **Dot separator**: Clear hierarchy, consistent with TOML sections
- **Underscore in platforms**: Follows Python naming conventions
- **Hyphen in channels**: Distinguishes from platform names, improves readability

## Inheritance Model

### Platforms with Inheritance

**bark, weixin, weixin_markdown_v2**:

```toml
[bark]
server_url = "https://api.day.app"
token = "default-token"

[bark.phone-1]
token = "phone1-token"
# Inherits: server_url from [bark]
```

### Platforms without Inheritance

**webhook**:

```toml
# Each webhook channel is independent
[webhook.slack-team1]
url = "https://hooks.slack.com/..."
method = "POST"

[webhook.slack-team2]
url = "https://hooks.slack.com/..."
method = "POST"
# Does NOT inherit from webhook.slack-team1
```

### Custom Platforms

For reusable webhook configurations:

```toml
[slack]
method = "POST"
body = '{"text": "{{title}}\\n{{message}}"}'

[slack.team1]
url = "https://hooks.slack.com/services/T11111111/..."
# Inherits: method and body from [slack]

[slack.team2]
url = "https://hooks.slack.com/services/T22222222/..."
# Inherits: method and body from [slack]
```

## API Shape

### Configuration

| Pattern | Example |
|---------|---------|
| Base platform | `[bark]` |
| Channel | `[bark.phone-1]` |
| Weixin markdown channel | `[weixin_markdown_v2.nbl-alerts]` |
| Webhook channel | `[webhook.slack-team1]` |

### Python API

| Pattern | Example |
|---------|---------|
| Base platform | `platform=owl_notify.platform.bark` |
| Channel helper | `platform=owl_notify.platform.bark.channel("phone-1")` |
| Weixin channel | `platform=owl_notify.platform.weixin.channel("team-alerts")` |
| Webhook channel | `platform=owl_notify.platform.webhook.channel("slack-team1")` |

## Testing

**Created `tests/test_new_api.py`**:
- Tests `PlatformChannel` class
- Tests platform constants
- Tests configuration parsing
- Tests platform routing
- All tests pass ✓

## Benefits

1. **Consistency**: All platforms use the same separator
2. **Clarity**: Clear distinction between platform and channel
3. **Readability**: `weixin.team-alerts` > `weixin_team_alerts`
4. **Type Safety**: Platform constants with IDE autocomplete
5. **Extensibility**: Easy to add new platforms and channels
6. **Maintainability**: Simpler code, fewer special cases

## Format Enforcement

- Only the new `platform.channel-name` format is supported for channels
- Entries that do not match the new format are shown as invalid in `owl -l`
- Built-in system sections like `[defaults]` and `[error]` are excluded from platform listings

## Files Modified

- `src/owl_notify/platform.py` - New `PlatformChannel` class
- `src/owl_notify/notify.py` - Updated parsing and routing
- `src/owl_notify/cli.py` - Updated list output
- `.owl-notify.toml.example` - New format examples
- `README.md` - Updated documentation

## Files Created

- `tests/test_new_api.py` - API tests
- `docs/REFACTORING_SUMMARY.md` - This file

## Next Steps

1. Update version to v0.2.0
2. Update CHANGELOG.md
3. Run full test suite
4. Update examples in repository
5. Release to PyPI

## Conclusion

This refactoring successfully unifies the naming convention across all platforms, making owl-notify more consistent, readable, and maintainable. The migration path is clear, and tools are provided to help users transition smoothly.
