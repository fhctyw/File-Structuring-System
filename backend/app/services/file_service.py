from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.file_descriptor import FileDescriptor

class FileService:
    @staticmethod
    def create_file_descriptor(db: Session, file_data: Dict[str, Any]) -> FileDescriptor:
        """Створити дескриптор файлу в базі даних."""
        # Перевірка, чи файл вже існує за хешем
        existing_file = db.query(FileDescriptor).filter(
            FileDescriptor.file_hash == file_data["file_hash"]
        ).first()
        
        if existing_file:
            return existing_file
            
        # Створення нового дескриптора файлу
        file_descriptor = FileDescriptor(**file_data)
        db.add(file_descriptor)
        db.commit()
        db.refresh(file_descriptor)
        
        return file_descriptor
        
    @staticmethod
    def get_file_descriptors(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        mime_type: Optional[str] = None
    ) -> List[FileDescriptor]:
        """Отримати дескриптори файлів з бази даних з опціональною фільтрацією."""
        query = db.query(FileDescriptor)
        
        if mime_type:
            query = query.filter(FileDescriptor.mime_type == mime_type)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_file_descriptor_by_hash(db: Session, file_hash: str) -> Optional[FileDescriptor]:
        """Отримати дескриптор файлу за його хешем."""
        return db.query(FileDescriptor).filter(
            FileDescriptor.file_hash == file_hash
        ).first()