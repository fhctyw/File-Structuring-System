from pathlib import Path

# Базова директорія додатку
BASE_DIR = Path(__file__).parent

# Налаштування бази даних
DATABASE_URL = f"sqlite:///{BASE_DIR}/file_structure.db"

DEBUG = True

# Налаштування API
API_PREFIX = "/api"
API_TITLE = "API структурування файлів"
API_DESCRIPTION = "API для структурування файлів у сховищі даних"
API_VERSION = "0.1.0"