from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from ..models.file_analysis import FileAnalysis
from ..models.file_descriptor import FileDescriptor
from ..utils.conf import current_config

class AnalysisService:
    """Створює або оновлює FileAnalysis."""

    @staticmethod
    def _meta_description(fd: FileDescriptor) -> str:
        return (f"{fd.filename} – size: {fd.size_bytes} B, type: {fd.file_type}, "
                f"mime: {fd.mime_type}")

    @staticmethod
    def _struct_description(fd: FileDescriptor) -> str:
        return (f"{fd.filename} structure: extension={fd.file_type}; path depth="
                f"{len(Path(fd.original_path).parts)}")

    @staticmethod
    def _semantic_description(fd: FileDescriptor) -> str:
        # TODO: Semantic analysis via AI model
        return f"{fd.filename}: semantic summary unavailable (stub)"

    @classmethod
    def analyse(cls, db: Session, descriptor: FileDescriptor, method_code: Optional[str] = None) -> FileAnalysis:
        method = method_code or current_config.analysis_method
        if method == "STRUCT":
            desc = cls._struct_description(descriptor)
        elif method == "SEMANTIC":
            desc = cls._semantic_description(descriptor)
        else:  # META by default
            desc = cls._meta_description(descriptor)

        analysis = FileAnalysis(file_hash=descriptor.file_hash, description=desc)
        db.merge(analysis)
        db.commit()
        return analysis