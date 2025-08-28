# DivoomDND Settings System Documentation

## Overview

The DivoomDND application uses a centralized settings system built around the `SettingsManager` class in `config.py`. This system provides persistent storage for all application configuration with an easy-to-use API.

## Architecture

### File Structure
```
config.py  ← Enhanced central settings manager
├── SettingsManager class (main settings engine)
├── get_settings() (global singleton access)
├── Backward compatibility functions
└── Structured settings with dot notation
```

### Settings File
- **Location**: `divoomdnd_settings.json` (in project root)
- **Format**: JSON with nested structure
- **Encoding**: UTF-8
- **Auto-created**: On first run with default values

## Settings Structure

```json
{
  "server": {
    "directory": "/path/to/serve",
    "port": 8000,
    "bind_address": "127.0.0.1",
    "auto_start": false
  },
  "gui": {
    "window_width": 600,
    "window_height": 400,
    "window_x": 100,
    "window_y": 100,
    "remember_window_position": true,
    "log_max_lines": 100
  },
  "pixoo": {
    "default_message": "Hello Pixoo!",
    "simulator_mode": false,
    "simulator_scale": 8,
    "auto_detect_device": true,
    "device_ip": null,
    "brightness": 100
  },
  "manual_priority": "lowest",
  "manual_status": null,
  "pixoo_settings": {}
}
```

## API Reference

### Basic Usage

```python
from config import get_settings, save_settings

# Get the global settings instance
settings = get_settings()

# Read values with dot notation
port = settings.get('server.port')                    # Returns: 8000
directory = settings.get('server.directory')          # Returns: "/path/to/serve"
brightness = settings.get('pixoo.brightness', 50)     # Returns: 100 (or 50 if not set)

# Set individual values
settings.set('server.port', 8080)
settings.set('pixoo.brightness', 75)

# Save to disk
save_settings()
```

### Advanced Usage

```python
# Get entire sections
server_config = settings.get_section('server')
# Returns: {'directory': '...', 'port': 8000, 'bind_address': '127.0.0.1', ...}

# Update multiple values in a section
settings.update_section('server', {
    'port': 8080,
    'directory': '/new/path',
    'auto_start': True
})

# Reset to defaults (entire config or specific section)
settings.reset_to_defaults()           # Reset everything
settings.reset_to_defaults('server')   # Reset just server section

# Save changes
save_settings()
```

### Error Handling

```python
# Settings gracefully handle missing keys
value = settings.get('nonexistent.key', 'default')  # Returns: 'default'

# Corrupted files fall back to defaults automatically
# Missing sections are created with default values
```

## Current Settings Categories

### Server Settings (`server.*`)
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `directory` | string | current working dir | Directory to serve files from |
| `port` | integer | 8000 | HTTP server port |
| `bind_address` | string | "127.0.0.1" | Network interface to bind to |
| `auto_start` | boolean | false | Start server automatically on app launch |

### GUI Settings (`gui.*`)
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `window_width` | integer | 600 | Main window width |
| `window_height` | integer | 400 | Main window height |
| `window_x` | integer | null | Window X position (null = OS decides) |
| `window_y` | integer | null | Window Y position (null = OS decides) |
| `remember_window_position` | boolean | true | Save/restore window position |
| `log_max_lines` | integer | 100 | Maximum lines in log display |

### Pixoo Settings (`pixoo.*`)
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_message` | string | "Hello Pixoo!" | Default text when input is empty |
| `simulator_mode` | boolean | false | Force simulator mode |
| `simulator_scale` | integer | 8 | Simulator display scale |
| `auto_detect_device` | boolean | true | Automatically find Pixoo device |
| `device_ip` | string | null | Manual device IP (when auto_detect is false) |
| `brightness` | integer | 100 | Display brightness (0-100) |

### Legacy Settings (backward compatibility)
| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `manual_priority` | string | "lowest" | Priority level for manual status |
| `manual_status` | string | null | Current manual status |
| `pixoo_settings` | object | {} | Legacy pixoo settings object |

## Implementation Examples

### Adding New Settings

1. **Add defaults** to `_defaults` in `config.py`:
```python
'new_feature': {
    'enabled': True,
    'timeout': 30,
    'color': '#FF0000'
}
```

2. **Use in your code**:
```python
settings = get_settings()
if settings.get('new_feature.enabled'):
    timeout = settings.get('new_feature.timeout')
    color = settings.get('new_feature.color')
```

3. **Save user changes**:
```python
settings.set('new_feature.enabled', False)
save_settings()
```

### GUI Integration Pattern

```python
class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.setup_ui()
        self.load_settings()
    
    def load_settings(self):
        """Load settings into UI controls"""
        self.checkbox.setChecked(self.settings.get('feature.enabled', True))
        self.spinbox.setValue(self.settings.get('feature.value', 10))
    
    def save_settings(self):
        """Save UI controls to settings"""
        self.settings.set('feature.enabled', self.checkbox.isChecked())
        self.settings.set('feature.value', self.spinbox.value())
        save_settings()
    
    def accept(self):
        """Called when OK is clicked"""
        self.save_settings()
        super().accept()
```

## Best Practices

### Naming Conventions
- Use lowercase with underscores: `auto_start`, `window_width`
- Group related settings in sections: `server.*`, `gui.*`, `pixoo.*`
- Use descriptive names: `remember_window_position` not `rem_pos`

### Default Values
- Always provide sensible defaults
- Use `null` for optional values that should be auto-determined
- Boolean settings should default to the safest/most conservative option

### Performance
- Settings are loaded once at startup and cached in memory
- Only call `save_settings()` when values actually change
- Use `update_section()` for multiple related changes

### Threading
- Settings manager is thread-safe (singleton pattern)
- GUI updates should happen on the main thread
- Server settings can be read from worker threads safely

## Troubleshooting

### Common Issues

**Settings not persisting:**
- Ensure you're calling `save_settings()` after changes
- Check file permissions on the settings file
- Verify the application has write access to the working directory

**Missing settings:**
- Settings automatically fall back to defaults for missing keys
- Check the `_defaults` dictionary in `config.py` for available settings
- Use `settings.get('key', fallback)` for safe access

**Corrupted settings file:**
- Delete `divoomdnd_settings.json` to reset to defaults
- The application will recreate the file with default values
- Consider implementing settings validation if corruption is frequent

### Debug Commands

```python
# Print all current settings
settings = get_settings()
import json
print(json.dumps(settings._settings, indent=2))

# Check if a setting exists
if settings.get('some.setting') is not None:
    print("Setting exists")

# Reset specific section for testing
settings.reset_to_defaults('server')
save_settings()
```

## Migration Guide

### From Old Config System
The old `load_config()` and `save_config()` functions are still supported but deprecated:

```python
# Old way (still works)
from config import load_config, save_config
config = load_config()
config['manual_priority'] = 'high'
save_config(config)

# New way (preferred)
from config import get_settings, save_settings
settings = get_settings()
settings.set('manual_priority', 'high')
save_settings()
```

### Updating Existing Code
1. Replace `load_config()` calls with `settings.get()`
2. Replace `save_config()` calls with `settings.set()` + `save_settings()`
3. Use dot notation for nested settings access
4. Add proper defaults to the `_defaults` dictionary

## Future Extensions

The settings system is designed to be easily extensible. Planned additions:

- Settings validation and type checking
- Settings export/import functionality
- Per-user settings profiles
- Environment variable overrides
- Settings change notifications/callbacks

---

*This documentation is for DivoomDND Settings System v1.0*
*Last updated: [Current Date]*