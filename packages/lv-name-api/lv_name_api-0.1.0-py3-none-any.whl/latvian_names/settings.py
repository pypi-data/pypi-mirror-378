import json
import os

SETTINGS_FILE = "settings.json"

DEFAULTS = {
    "output_format": "table",
    "max_results": 10
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f), False
        except Exception:
            return DEFAULTS.copy(), True
    return DEFAULTS.copy(), True

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
