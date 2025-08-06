#	Resolves status based on priority
from config import load_config

def get_current_status():
    config = load_config()
    return config.get('manual_status', 'default status')
