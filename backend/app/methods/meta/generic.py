from pathlib import Path
from app.core.base import MethodExtractor

class TypeExtractor(MethodExtractor):
    def run(self, file_info):
        return {
            "real_extension": Path(file_info["filename"]).suffix.lstrip("."),
            "mime_type": file_info["mime_type"]
        }