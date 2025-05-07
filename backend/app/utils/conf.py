import json
from pathlib import Path
from ..config import BASE_DIR

CONF_PATH = BASE_DIR / "conf.json"

class Config:
    """Читає conf.json та зберігає активні метод / алгоритм."""
    def __init__(self):
        self.reload()

    def reload(self):
        if not CONF_PATH.exists():
            self.analysis_method  = "META"
            self.struct_algorithm = "BY_TYPE"
            return
        data = json.loads(CONF_PATH.read_text(encoding="utf‑8"))
        self.analysis_method  = data.get("active_analysis_method", "META")
        self.struct_algorithm = data.get("active_struct_algorithm", "BY_TYPE")

current_config = Config()