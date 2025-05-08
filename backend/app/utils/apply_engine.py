import os, shutil
from typing import Dict

def apply_instruction(instr: Dict) -> Dict:
    """
    Застосовує інструкцію для файлової системи.
    
    Args:
        instr: Словник з інструкцією, що містить дію, параметри та file_path
        
    Returns:
        Dict: Результат виконання з полями status та, опціонально, error
    """
    action = instr["action"]
    params = instr["params"]
    
    try:
        if action == "CREATE_DIR":
            # Створюємо директорію, якщо вона не існує
            path = params.get("path", "")
            if not path:
                return {"status": "FAILED", "error": "Path not specified for CREATE_DIR"}
            
            os.makedirs(path, exist_ok=True)
            return {"status": "APPLIED"}
            
        elif action == "DELETE_EMPTY_DIR":
            # Перевіряємо, що директорія існує і дійсно пуста
            path = params.get("path", "")
            if not path:
                return {"status": "FAILED", "error": "Path not specified for DELETE_EMPTY_DIR"}
            
            if not os.path.isdir(path):
                return {"status": "FAILED", "error": f"Directory does not exist: {path}"}
            
            # Перевіряємо, що директорія дійсно пуста
            if not os.listdir(path):
                os.rmdir(path)
                return {"status": "APPLIED"}
            else:
                return {"status": "FAILED", "error": f"Directory is not empty: {path}"}
                
        elif action == "MOVE_FILE":
            # Перевіряємо наявність вихідного файлу
            src = params.get("src", "")
            if not src:
                return {"status": "FAILED", "error": "Source path not specified for MOVE_FILE"}
            
            # Отримуємо шлях призначення
            dst = params.get("dst", "")
            if not dst:
                return {"status": "FAILED", "error": "Destination path not specified for MOVE_FILE"}
            
            # Перевіряємо, що вихідний файл існує
            if not os.path.isfile(src):
                return {"status": "FAILED", "error": f"Source file does not exist: {src}"}
            
            # Переконуємося, що цільова директорія існує
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            # Рухаємо файл
            shutil.move(src, dst)
            return {"status": "APPLIED"}
            
        elif action == "RENAME_FILE":
            # Перевіряємо наявність вихідного файлу
            src = params.get("src", "")
            if not src:
                return {"status": "FAILED", "error": "Source path not specified for RENAME_FILE"}
            
            # Отримуємо цільовий шлях
            dst = params.get("dst", "")
            if not dst:
                return {"status": "FAILED", "error": "Destination path not specified for RENAME_FILE"}
            
            # Перевіряємо, що вихідний файл існує
            if not os.path.exists(src):
                return {"status": "FAILED", "error": f"Source file does not exist: {src}"}
            
            # Переконуємося, що цільова директорія існує
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            # Перейменовуємо файл
            os.rename(src, dst)
            return {"status": "APPLIED"}
            
        else:
            return {"status": "FAILED", "error": f"Unknown action: {action}"}
            
    except Exception as exc:
        return {"status": "FAILED", "error": str(exc)}