from abc import ABC, abstractmethod
from typing import Dict, List


class MethodExtractor(ABC):
    """1-й шар: робить опис окремого файлу."""
    @abstractmethod
    def run(self, file_info: Dict) -> Dict:
        """file_info = повертає dict-опис."""


class StructAlgorithm(ABC):
    """2-й шар: зі списку описів робить інструкції."""
    @abstractmethod
    def run(self, descriptions: List[Dict]) -> List[Dict]:
        """
        descriptions -> [{'file_hash':..., ...}, ...]
        return [ { "file_hash": "...",
                   "action": "MOVE_FILE",
                   "params": { "dst": "Images/…" } }, ... ]
        """
