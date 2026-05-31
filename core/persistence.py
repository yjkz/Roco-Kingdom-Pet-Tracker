import json
import os
import sys
from models.pokemon_data import AppConfig

# data saved next to exe (frozen) or in plugin dir (Python)
if getattr(sys, 'frozen', False):
    _DATA_DIR = os.path.join(os.path.dirname(sys.executable), "data")
else:
    _DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

DATA_FILE = os.path.join(_DATA_DIR, "data.json")
CACHE_DIR = os.path.join(_DATA_DIR, "thumbnails")


def ensure_dirs():
    os.makedirs(_DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_config() -> AppConfig:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return AppConfig.from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    default_path = os.path.join(os.path.dirname(__file__), "..", "resources", "default_config.json")
    with open(default_path, "r", encoding="utf-8") as f:
        return AppConfig.from_dict(json.load(f))


def save_config(config: AppConfig):
    ensure_dirs()
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, DATA_FILE)
