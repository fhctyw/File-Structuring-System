from abc import ABC, abstractmethod
from typing import Dict, List


class MethodExtractor(ABC):
    @abstractmethod
    def run(self, file_info: Dict) -> Dict:
        """file_info = повертає dict-опис."""


class StructAlgorithm(ABC):
    @abstractmethod
    def run(self, descriptions: List[Dict]) -> List[Dict]:
        """
        descriptions = список dict-описів, які потрібно обробити.
        return = cписок dict-інструкцій, які потрібно буде виконати.
        """
