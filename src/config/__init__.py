import json
from pathlib import Path

_CONFIG_DIR = Path(__file__).resolve().parent

with open(_CONFIG_DIR / "normalization_rules.json", "r", encoding="utf-8") as f:
    normalization_config = json.load(f)

with open(_CONFIG_DIR / "filters_config.json", "r", encoding="utf-8") as f:
    filters_config = json.load(f)


def load_stylesheet(app, filename: str = "style.qss") -> None:
    """
    Load a Qt Style Sheet (QSS) file from the config package and apply it.
    """
    qss_path = Path(__file__).resolve().parent / filename
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


__all__ = ["normalization_config", "filters_config"]
