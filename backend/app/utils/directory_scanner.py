import os
from typing import List, Dict
from .file_analyzer import create_file_descriptor

def scan_dir(directory: str, recursive: bool = False) -> list:
    """
    Сканувати директорію та повернути список файлових дескрипторів.
    
    Args:
        directory (str): Шлях до директорії для сканування
        recursive (bool): Чи сканувати підкаталоги рекурсивно
        
    Returns:
        list: Список файлових дескрипторів
    """
    # Перевірка наявності директорії
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Директорію не знайдено: {directory}")
    
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Не є директорією: {directory}")
    
    file_descriptors = []
    
    # Визначення файлів для сканування в залежності від параметра recursive
    if recursive:
        # Обхід директорії та всіх піддиректорій
        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    file_descriptor = create_file_descriptor(file_path)
                    file_descriptors.append(file_descriptor)
                except Exception as e:
                    print(f"Помилка обробки файлу {file_path}: {e}")
    else:
        # Сканування тільки файлів верхнього рівня
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                try:
                    file_descriptor = create_file_descriptor(item_path)
                    file_descriptors.append(file_descriptor)
                except Exception as e:
                    print(f"Помилка обробки файлу {item_path}: {e}")
    
    return file_descriptors
