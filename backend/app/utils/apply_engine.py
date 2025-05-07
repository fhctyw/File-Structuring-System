import os, shutil
from datetime import datetime
from typing import Dict

def apply_instruction(instr: Dict) -> Dict:
    """
    Виконує одну інструкцію; повертає {"status": "APPLIED"/"FAILED", "error":...}
    """
    action = instr["action"]
    params = instr["params"]
    try:
        if action == "CREATE_DIR":
            os.makedirs(params["path"], exist_ok=True)
        elif action == "DELETE_EMPTY_DIR":
            if os.path.isdir(params["path"]) and not os.listdir(params["path"]):
                os.rmdir(params["path"])
        elif action == "MOVE_FILE":
            shutil.move(params["src"], params["dst"])
        elif action == "RENAME_FILE":
            os.rename(params["src"], params["dst"])
        return {"status": "APPLIED", "applied_at": datetime.utcnow()}
    except Exception as exc:
        return {"status": "FAILED", "error": str(exc), "applied_at": datetime.utcnow()}