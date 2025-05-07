import os
import hashlib
import platform
import mimetypes
from typing import Dict, Any

# Адаптуємо імпорт magic для різних ОС
try:
    import magic
    has_magic = True
except ImportError:
    has_magic = False
    try:
        # Спробуємо альтернативний варіант для Windows
        import magic_win as magic
        has_magic = True
    except ImportError:
        print("Увага: Бібліотеку 'magic' не знайдено. Використовуємо базові методи визначення типу файлу.")
        # Ініціалізуємо mimetypes
        mimetypes.init()

def get_file_hash(file_path: str) -> str:
    """Обчислити хеш SHA-256 файлу."""
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Читати та оновлювати хеш блоками по 4К
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return sha256_hash.hexdigest()

def get_file_type(file_path: str) -> str:
    """Визначити тип файлу використовуючи magic."""
    system = platform.system()
    
    try:
        if has_magic:
            # Використовуємо різні версії magic в залежності від ОС
            if system == "Windows":
                # На Windows часто використовується інша сигнатура
                try:
                    m = magic.Magic()
                    return m.from_file(file_path)
                except (AttributeError, TypeError):
                    # Якщо не працює, спробуємо python-magic-bin підхід
                    return magic.from_file(file_path)
            else:
                # Linux/Mac підхід
                try:
                    m = magic.Magic()
                    return m.from_file(file_path)
                except (AttributeError, TypeError):
                    # Альтернативний API
                    return magic.from_file(file_path)
        else:
            # Якщо magic недоступний, повертаємо UNKNOWN
            return "UNKNOWN"
    except Exception as e:
        print(f"Помилка визначення типу для {file_path}: {e}")
        # Запасний варіант - визначення за розширенням
        ext = os.path.splitext(file_path)[1].lower()
        if ext:
            return f"EXTENSION: {ext.lstrip('.')}"
        return "UNKNOWN"

def get_mime_type(file_path: str) -> str:
    """Визначити MIME тип файлу за розширенням."""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"

def get_file_size(file_path: str) -> int:
    """Отримати розмір файлу в байтах."""
    return os.path.getsize(file_path)

def create_file_descriptor(file_path: str) -> Dict[str, Any]:
    """Створити дескриптор файлу з метаданими."""
    abs_path = os.path.abspath(file_path)
    file_hash = get_file_hash(abs_path)
    
    return {
        "file_hash": file_hash,
        "filename": os.path.basename(abs_path),
        "original_path": abs_path,
        "file_type": get_file_type(abs_path),
        "mime_type": get_mime_type(abs_path),
        "size_bytes": get_file_size(abs_path)
    }