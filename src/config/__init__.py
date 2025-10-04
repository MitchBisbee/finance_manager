import json
from pathlib import Path

# Path to this directory
_CONFIG_DIR = Path(__file__).resolve().parent

# Preload the normalization config
with open(_CONFIG_DIR / "normalization_rules.json", "r", encoding="utf-8") as f:
    normalization_config = json.load(f)

__all__ = ["normalization_config"]
