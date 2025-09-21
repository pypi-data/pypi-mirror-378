import yaml
import importlib.resources as pkg_resources
from harsh_ai_assistant import config  # your config package

def load_settings():
    """Load settings.yaml from the installed package."""
    with pkg_resources.open_text(config, "settings.yaml") as f:
        settings = yaml.safe_load(f)
    return settings
