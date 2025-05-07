import os
from typing import List, Dict, Any

from ..utils.file_analyzer import create_file_descriptor

class DirectoryService:
    @staticmethod
    def scan_directory(directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Сканувати директорію та отримати дескриптори файлів."""
        directory_path = os.path.abspath(directory_path)
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Директорію не знайдено: {directory_path}")
            
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Не є директорією: {directory_path}")
            
        file_descriptors = []
        
        if recursive:
            for root, _, files in os.walk(directory_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    try:
                        file_descriptor = create_file_descriptor(file_path)
                        file_descriptors.append(file_descriptor)
                    except Exception as e:
                        # Логування помилки та продовження
                        print(f"Помилка обробки файлу {file_path}: {e}")
        else:
            for entry in os.scandir(directory_path):
                if entry.is_file():
                    try:
                        file_descriptor = create_file_descriptor(entry.path)
                        file_descriptors.append(file_descriptor)
                    except Exception as e:
                        # Логування помилки та продовження
                        print(f"Помилка обробки файлу {entry.path}: {e}")
                        
        return file_descriptors