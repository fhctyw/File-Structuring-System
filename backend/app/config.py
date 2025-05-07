import os
from pathlib import Path
from typing import Dict, List

# Базова директорія додатку
BASE_DIR = Path(__file__).parent

# Налаштування бази даних
DATABASE_URL = f"sqlite:///{BASE_DIR}/file_structure.db"
FRONTEND_URL = "127.0.0.1:3000"

DEBUG = True

# Налаштування API
API_PREFIX = "/api"
API_TITLE = "API структурування файлів"
API_DESCRIPTION = "API для структурування файлів у сховищі даних"
API_VERSION = "0.1.0"

# Налаштування за замовчуванням
DEFAULT_CONFIG = {
    "supported_file_types": {
        "images": ["jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff"],
        "documents": ["pdf", "docx", "doc", "txt", "rtf", "odt"],
        "audio": ["mp3", "wav", "ogg", "flac", "aac"],
        "video": ["mp4", "avi", "mkv", "mov", "wmv"],
        "archives": ["zip", "rar", "7z", "tar", "gz"]
    }
}

# Шлях до файлу користувацької конфігурації
USER_CONFIG_PATH = BASE_DIR / "user_config.json"