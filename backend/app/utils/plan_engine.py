from pathlib import Path
from typing import Dict, List, Set

def build_plan(descriptors: List[Dict], algorithm: str) -> List[Dict]:
    instructions: List[Dict] = []

    if algorithm == "BY_TYPE":
        created_dirs: Set[str] = set()

        for d in descriptors:
            target_dir = Path(d["original_path"]).parent / d["file_type"]

            # 1. CREATE_DIR – один раз на розширення
            if str(target_dir) not in created_dirs:
                instructions.append({
                    "file_hash": d["file_hash"],          # будь‑який hash, не критично
                    "action": "CREATE_DIR",
                    "params": {"path": str(target_dir)}
                })
                created_dirs.add(str(target_dir))

            # 2. MOVE_FILE
            instructions.append({
                "file_hash": d["file_hash"],
                "action": "MOVE_FILE",
                "params": {
                    "src": d["original_path"],
                    "dst": str(target_dir / d["filename"])
                }
            })
        return instructions

    if algorithm == "CLUSTER":
        # TODO
        pass
    if algorithm == "CRITERIA":
        # TODO
        pass

    return instructions