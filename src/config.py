"""Load YAML config files from config/."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def _load(name):
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def sources():
    return _load("sources.yaml")


def criteria():
    return _load("criteria.yaml")


def settings():
    return _load("settings.yaml")
