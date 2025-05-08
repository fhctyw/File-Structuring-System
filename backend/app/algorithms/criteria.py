import os
from typing import Dict, List
from app.core.base import StructAlgorithm
from app.models.file_instruction import ActionType

class CriteriaAlgorithm(StructAlgorithm):
    def __init__(self, field="mime_type"):
        self.field = field                # параметр може надходити із params_schema

    def run(self, descriptions: List[Dict]) -> List[Dict]:
        """
        Створює інструкції для групування файлів за реальним розширенням.
        
        Args:
            descriptions: Список описів файлів (з method_extractor.run)
            
        Returns:
            List[Dict]: Список інструкцій для виконання
        """
        # Результуючий список інструкцій
        instructions = []
        
        # Мапа для групування файлів за розширеннями
        file_extensions = {}
        
        # Множина директорій, які потрібно створити
        dirs_to_create = set()

        # Отримуємо базову директорію (припускаємо, що всі файли знаходяться в одній базовій директорії)
        base_dir = None
        for desc in descriptions:
            if "original_path" in desc:
                base_dir = os.path.dirname(os.path.dirname(desc["original_path"]))
                break
        
        if not base_dir:
            # Якщо не вдалося отримати базову директорію, використовуємо поточну
            base_dir = os.getcwd()
        
        # Класифікуємо файли за їх розширеннями
        for desc in descriptions:
            # Оригінальний шлях до файлу 
            original_path = desc.get("original_path")
            
            # Отримуємо розширення файлу
            extension = desc.get("real_extension", "").lower()
            if not extension:
                extension = "unknown"
            
            # Визначаємо категорію для файлу
            category = self._get_category_for_extension(extension)
            
            # Додаємо файл до відповідної категорії
            if category not in file_extensions:
                file_extensions[category] = []
            
            if original_path:
                file_extensions[category].append({
                    "path": original_path,
                    "extension": extension
                })
            
            # Додаємо директорію до множини директорій, які потрібно створити
            dirs_to_create.add(category)
        
        # Створюємо інструкції для створення директорій
        for dir_name in dirs_to_create:
            # Створюємо повний шлях до нової директорії
            full_dir_path = os.path.join(base_dir, dir_name)
            
            instructions.append({
                "file_path": full_dir_path,  # Повний шлях до нової директорії
                "action": ActionType.CREATE_DIR,
                "params": {
                    "path": dir_name
                }
            })
        
        # Створюємо інструкції для переміщення файлів
        for category, files in file_extensions.items():
            for file_info in files:
                if not file_info["path"]:
                    continue  # Пропускаємо файли без шляху
                    
                instructions.append({
                    "file_path": file_info["path"],  # Повний шлях до файлу
                    "action": ActionType.MOVE_FILE,
                    "params": {
                        "dst": os.path.join(category, "")  # Цільова директорія
                    }
                })
        
        return instructions
    
    def _get_category_for_extension(self, extension: str) -> str:
        """
        Визначає категорію директорії для заданого розширення файлу.
        
        Args:
            extension: Розширення файлу (без крапки)
            
        Returns:
            str: Назва категорії (шлях до директорії)
        """
        # Словник категорій за розширеннями
        extension_categories = {
            # Зображення
            "jpg": "Images",
            "jpeg": "Images",
            "png": "Images",
            "gif": "Images",
            "bmp": "Images",
            "tiff": "Images",
            "svg": "Images",
            "webp": "Images",
            "ico": "Images",
            
            # Документи
            "doc": "Documents/Word",
            "docx": "Documents/Word",
            "pdf": "Documents/PDF",
            "txt": "Documents/Text",
            "rtf": "Documents/Text",
            "odt": "Documents/Word",
            
            # Таблиці
            "xls": "Documents/Excel",
            "xlsx": "Documents/Excel",
            "csv": "Documents/Excel",
            "ods": "Documents/Excel",
            
            # Презентації
            "ppt": "Documents/PowerPoint",
            "pptx": "Documents/PowerPoint",
            "odp": "Documents/PowerPoint",
            
            # Код
            "py": "Code/Python",
            "js": "Code/JavaScript",
            "html": "Code/Web",
            "css": "Code/Web",
            "java": "Code/Java",
            "c": "Code/C",
            "cpp": "Code/C++",
            "h": "Code/Headers",
            "json": "Code/Data",
            "xml": "Code/Data",
            
            # Архіви
            "zip": "Archives",
            "rar": "Archives",
            "tar": "Archives",
            "gz": "Archives",
            "7z": "Archives",
            
            # Виконувані файли
            "exe": "Executables/Windows",
            "dll": "Executables/Windows",
            "bat": "Executables/Windows",
            "sh": "Executables/Unix",
            "app": "Executables/Mac",
            
            # Аудіо
            "mp3": "Audio",
            "wav": "Audio",
            "ogg": "Audio",
            "flac": "Audio",
            "aac": "Audio",
            
            # Відео
            "mp4": "Video",
            "avi": "Video",
            "mkv": "Video",
            "mov": "Video",
            "wmv": "Video",
            
            # Конфігурації
            "ini": "Config",
            "yaml": "Config",
            "yml": "Config",
            "toml": "Config",
            "conf": "Config",
            
            # Бази даних
            "db": "Databases",
            "sqlite": "Databases",
            "sql": "Databases",
            
            # Шрифти
            "ttf": "Fonts",
            "otf": "Fonts",
            "woff": "Fonts",
            "woff2": "Fonts",
        }
        
        # Повертаємо категорію за розширенням або 'Other' якщо розширення невідоме
        return extension_categories.get(extension, "Other")
