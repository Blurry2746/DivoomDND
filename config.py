#Manages persistent configuration settings
import json, os

CONFIG_FILE = 'config.json'
default_config = {
    'manual_priority': 'lowest',
    'manual_status': None,
    'pixoo_settings': {}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return default_config.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
