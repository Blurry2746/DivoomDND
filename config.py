# Manages persistent configuration settings for the entire application
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class SettingsManager:
    """Centralized settings manager for all application settings"""

    def __init__(self, config_file: str = 'divoomdnd_settings.json'):
        self.config_file = config_file
        self._settings = {}
        self._defaults = {
            # Original settings
            'manual_priority': 'lowest',
            'manual_status': None,
            'pixoo_settings': {},

            # HTTP Server settings
            'server': {
                'directory': str(Path.cwd()),
                'port': 8000,
                'bind_address': '127.0.0.1',
                'auto_start': False
            },

            # GUI settings
            'gui': {
                'window_width': 600,
                'window_height': 400,
                'window_x': None,  # Let OS decide initial position
                'window_y': None,
                'log_max_lines': 100,
                'remember_window_position': True
            },

            # Pixoo settings (extensible)
            'pixoo': {
                'default_message': 'Hello Pixoo!',
                'simulator_mode': False,
                'simulator_scale': 8,
                'auto_detect_device': True,
                'device_ip': None,
                'brightness': 100,
                'uploaded_gifs': []  # Track uploaded GIFs
            }
        }
        self.load()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        Examples:
            get('server.port') -> 8000
            get('gui.window_width') -> 600
            get('pixoo.brightness') -> 100
        """
        keys = key.split('.')
        value = self._settings

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Try to get from defaults
            try:
                value = self._defaults
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value using dot notation.
        Examples:
            set('server.port', 8080)
            set('gui.window_width', 800)
            set('pixoo.brightness', 75)
        """
        keys = key.split('.')
        current = self._settings

        # Navigate/create nested structure
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire settings section.
        Examples:
            get_section('server') -> {'directory': '...', 'port': 8000, ...}
            get_section('gui') -> {'window_width': 600, ...}
        """
        return self.get(section, {})

    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        Update multiple values in a section at once.
        Examples:
            update_section('server', {'port': 8080, 'directory': '/path'})
            update_section('gui', {'window_width': 800, 'window_height': 600})
        """
        for key, value in values.items():
            self.set(f"{section}.{key}", value)

    def load(self) -> None:
        """Load settings from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Merge with defaults to ensure all keys exist
                self._settings = self._merge_with_defaults(loaded_settings)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings from {self.config_file}: {e}")
                self._settings = self._defaults.copy()
        else:
            # Use defaults for first run
            self._settings = self._defaults.copy()

    def save(self) -> None:
        """Save current settings to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)

        except IOError as e:
            print(f"Error: Could not save settings to {self.config_file}: {e}")

    def reset_to_defaults(self, section: Optional[str] = None) -> None:
        """
        Reset settings to defaults.
        If section is specified, only reset that section.
        """
        if section:
            if section in self._defaults:
                self._settings[section] = self._defaults[section].copy()
        else:
            self._settings = self._defaults.copy()

    def _merge_with_defaults(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge loaded settings with defaults"""

        def merge_dict(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result

        return merge_dict(self._defaults, loaded)


# Global settings instance - singleton pattern
_settings_instance = None


def get_settings() -> SettingsManager:
    """Get the global settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance


def save_settings() -> None:
    """Convenient function to save settings"""
    get_settings().save()


# Backward compatibility functions for existing code
def load_config() -> Dict[str, Any]:
    """Load config (backward compatibility)"""
    settings = get_settings()
    return {
        'manual_priority': settings.get('manual_priority'),
        'manual_status': settings.get('manual_status'),
        'pixoo_settings': settings.get('pixoo_settings', {})
    }


def save_config(config: Dict[str, Any]) -> None:
    """Save config (backward compatibility)"""
    settings = get_settings()
    if 'manual_priority' in config:
        settings.set('manual_priority', config['manual_priority'])
    if 'manual_status' in config:
        settings.set('manual_status', config['manual_status'])
    if 'pixoo_settings' in config:
        settings.set('pixoo_settings', config['pixoo_settings'])
    settings.save()