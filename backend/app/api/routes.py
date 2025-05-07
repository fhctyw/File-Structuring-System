from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from ..database import get_db
from ..services.session_service import SessionService
from ..schemas import session_schemas as sch

router = APIRouter(tags=["Structuring Sessions"])

# ---------- Довідники ----------
@router.get("/analysis-methods", response_model=List[Dict[str, Any]])
def get_analysis_methods():
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

@router.get("/sessions/{session_id}", response_model=sch.SessionDetail)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    sess = SessionService.get_session(db, session_id)
    if not sess:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return sess

# ---------- 2. Аналіз ----------
@router.post("/sessions/{session_id}/analyze", response_model=sch.AnalysisSummary)
def run_analysis(
    session_id: UUID,
    payload: sch.AnalysisRequest,
    db: Session = Depends(get_db)
):
    summary = SessionService.run_analysis(db, session_id, payload.method)
    if summary is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return summary

# ---------- 3. План ----------
@router.post("/sessions/{session_id}/plan", response_model=sch.PlanSummary)
def generate_plan(
    session_id: UUID,
    payload: sch.PlanRequest,
    db: Session = Depends(get_db)
):
    plan = SessionService.generate_plan(db, session_id, payload.algorithm)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return plan

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
