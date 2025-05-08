import json
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query, Path as FsPath
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from app.models.algorithm_registry import AlgorithmRegistry
from app.models.method_registry import MethodRegistry

from ..database import get_db
from ..services.session_service import SessionService
from ..schemas import session_schemas as sch

router = APIRouter(tags=["Structuring Sessions"])

# ---------- Довідники ----------
@router.get(
    "/analysis-methods",
    response_model=Dict[str, List[sch.MethodSchema]]
)
async def get_analysis_methods():
    return SessionService.get_analysis_methods()

@router.get("/struct-algorithms", response_model=List[Dict[str, Any]])
def get_struct_algorithms():
    return SessionService.get_struct_algorithms()

@router.get("/fs/entries", response_model=Dict[str, Any])
def get_fs_entries(dir: str = Query(..., description="Absolute directory path")):
    try:
        return {"directory": dir, "entries": SessionService.get_fs_entries(dir)}
    except Exception as exc:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))

# ---------- 1. Сесії ----------
@router.post("/sessions/", status_code=status.HTTP_201_CREATED,
             response_model=sch.SessionShort)
def create_session(
    payload: sch.SessionCreate,
    db: Session = Depends(get_db)
):
    return SessionService.create_session(db, payload)

@router.get("/sessions/", response_model=List[sch.SessionShort])
def list_sessions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return SessionService.list_sessions(db, skip, limit)

@router.get(
    "/sessions/{session_id}",
    # response_model=sch.SessionDetail
)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    print(f"SEISSION_ID: {session_id}")
    sess = SessionService.get_session(db, session_id)
    if not sess:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return sess

@router.post("/sessions/{session_id}/process", response_model=sch.ProcessSummary)
def analyze_and_plan(
    session_id: UUID,
    payload: sch.ProcessRequest,
    db: Session = Depends(get_db)
):
    try:
        summary = SessionService.analyze_and_plan(db, session_id,
                                                payload.method,
                                                payload.algorithm)
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    if summary is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return summary

# ---------- 4. Прев’ю ----------
@router.get("/sessions/{session_id}/preview", response_model=sch.PreviewTree)
def preview(session_id: UUID, db: Session = Depends(get_db)):
    tree = SessionService.get_preview(db, session_id)
    if tree is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return tree

# ---------- 5. Застосування ----------
@router.post("/sessions/{session_id}/apply", response_model=sch.ApplyResult)
def apply_plan(
    session_id: UUID,
    payload: sch.ApplyRequest = Body(...),
    db: Session = Depends(get_db)
):
    
    result = SessionService.apply_plan(db, session_id, payload.dry_run)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session or plan not found")
    return result

# ---------- 6. Прогрес ----------
@router.get("/sessions/{session_id}/progress", response_model=sch.ProgressReport)
def get_progress(session_id: UUID, db: Session = Depends(get_db)):
    progress = SessionService.get_progress(db, session_id)
    if progress is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return progress

@router.post("/admin/sync-methods")
def sync_methods(db: Session = Depends(get_db)):
    methods_dict = SessionService.get_analysis_methods()

    added = []
    for group, methods in methods_dict.items():
        for method in methods:
            method_id = method["id"]

            exists = db.query(MethodRegistry).filter_by(id=method_id).first()
            if not exists:
                new_method = MethodRegistry(
                    id=method_id,
                    description=method.get("description", ""),
                    layer=method.get("layer", "META"),
                    domain=method.get("domain", "GENERIC"),
                    action=method.get("action", "NONE"),
                    returns=json.dumps(method.get("returns", [])),
                    impl_class=method.get("impl_class", ""),
                    enabled=method.get("enabled", True)
                )
                db.add(new_method)
                added.append(method_id)
                print(f"Added new method to DB: {method_id}")
            else:
                return {
                    "status": "already_exists",
                    "method_id": method_id
                }

    db.commit()
    return {
        "status": "ok",
        "added": added,
        "total_added": len(added)
    }
    
@router.post("/admin/sync-algorithms")
def sync_algorithms(db: Session = Depends(get_db)):
    algorithms_list = SessionService.get_struct_algorithms()

    added = []
    for algo in algorithms_list:
        algo_id = algo["id"]

        exists = db.query(AlgorithmRegistry).filter_by(id=algo_id).first()
        if not exists:
            new_algo = AlgorithmRegistry(
                id=algo_id,
                description=algo.get("description", ""),
                params_schema=json.dumps(algo.get("params_schema", {})),
                scope=algo.get("scope", "*"),
                impl_class=algo.get("impl_class", ""),
                enabled=algo.get("enabled", True)
            )
            db.add(new_algo)
            added.append(algo_id)
            print(f"Added new algorithm to DB: {algo_id}")
        else:
            return {
                "status": "already_exists",
                "algorithm_id": algo_id
            }

    db.commit()
    return {
        "status": "ok",
        "added": added,
        "total_added": len(added)
    }