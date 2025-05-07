# app/services/session_service.py
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any, Optional
import os

from sqlalchemy.orm import Session as DBSession

from app.schemas.session_schemas import SessionCreate

from ..models.struct_session import StructSession, SessionStatus
from ..models.file_descriptor import FileDescriptor
from ..models.file_analysis import FileAnalysis
from ..models.file_instruction import FileInstruction, ActionType, InstructionStatus

from ..utils.directory_scanner import scan as scan_dir
from ..utils.analysis_engine   import make_description
from ..utils.plan_engine       import build_plan
from ..utils.apply_engine      import apply_instruction


class SessionService:
    # ---------- Довідники ----------
    @staticmethod
    def get_analysis_methods() -> List[Dict[str, Any]]:
        return [{"code": c} for c in ["META", "STRUCT", "SEMANTIC"]]

    @staticmethod
    def get_struct_algorithms() -> List[Dict[str, Any]]:
        return [{"code": c} for c in ["BY_TYPE", "CLUSTER", "CRITERIA"]]

    @staticmethod
    def get_fs_entries(dir_path: str) -> List[str]:
        return os.listdir(dir_path)


    # ---------- CRUD сесій ----------
    @staticmethod
    def create_session(db: DBSession, payload: SessionCreate) -> Dict[str, Any]:
        sess = StructSession(
            directory = payload.directory,
            recursive = payload.recursive,
            status    = SessionStatus.NEW
        )
        
        db.add(sess)
        db.commit(); db.refresh(sess)
        return {
            "id": sess.id,
            "directory": sess.directory,
            "status": sess.status,
            "created_at": sess.created_at
        }

    @staticmethod
    def list_sessions(db: DBSession, skip=0, limit=50):
        return db.query(StructSession).offset(skip).limit(limit).all()

    @staticmethod
    def get_session(db: DBSession, sid):
        return db.query(StructSession).filter(StructSession.id == sid).first()


    # ---------- ANALYZE ----------
    @staticmethod
    def run_analysis(db: DBSession, sid, method) -> Optional[Dict]:
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None

        sess.status = SessionStatus.ANALYZING
        db.commit()

        # 1. скануємо каталоги
        desc_list = scan_dir(sess.directory, sess.recursive)
        sess.files_total = len(desc_list)

        # 2. дескриптори
        for d in desc_list:
            db.add(FileDescriptor(session_id=sid, **d))

        # 3. аналіз
        examples = []
        for d in desc_list[:3]:
            desc = make_description(d, method)
            examples.append(desc)
            db.add(FileAnalysis(session_id=sid, file_hash=d["file_hash"], description=desc))

        sess.analysis_method = method
        sess.status = SessionStatus.ANALYZED
        db.commit()
        return {"files_analyzed": sess.files_total, "description_examples": examples}


    # ---------- PLAN ----------
    @staticmethod
    def generate_plan(db: DBSession, sid, algorithm) -> Optional[Dict]:
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None

        descriptors = db.query(FileDescriptor).filter(FileDescriptor.session_id == sid).all()
        instr_list = build_plan([d.__dict__ for d in descriptors], algorithm)

        for instr in instr_list:
            db.add(
                FileInstruction(
                    session_id=sid,
                    file_hash=instr["file_hash"],
                    action=instr["action"],
                    params=instr["params"]
                )
            )

        sess.struct_algorithm = algorithm
        sess.actions_total = len(instr_list)
        sess.status = SessionStatus.PLANNED
        db.commit()
        return {"actions_created": sess.actions_total, "breakdown": {"total": sess.actions_total}}


    # ---------- PREVIEW ----------
    @staticmethod
    def get_preview(db: DBSession, sid) -> Optional[Dict]:
        instr = db.query(FileInstruction).filter(
            FileInstruction.session_id == sid,
            FileInstruction.action == ActionType.MOVE_FILE
        ).all()
        if not instr:
            return None

        tree: Dict[str, Any] = {}
        for i in instr:
            dst = Path(i.params["dst"]).relative_to(Path(i.params["dst"]).anchor)
            parts = dst.parts
            node = tree
            for p in parts:
                node = node.setdefault(p, {})
        return {"tree": tree}



    # ---------- APPLY ----------
    @staticmethod
    def apply_plan(db: DBSession, sid, dry_run=False) -> Optional[Dict]:
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None

        instrs = db.query(FileInstruction).filter(
            FileInstruction.session_id == sid,
            FileInstruction.status == InstructionStatus.PENDING
        ).all()

        applied = failed = 0
        errors: List[str] = []

        for instr in instrs:
            # заповнюємо src для MOVE/RENAME
            if instr.action in {ActionType.MOVE_FILE, ActionType.RENAME_FILE}:
                fd = db.query(FileDescriptor).filter(FileDescriptor.file_hash == instr.file_hash).first()
                if fd:
                    instr.params.setdefault("src", fd.original_path)

            if dry_run:
                continue

            result = apply_instruction(instr.__dict__)
            instr.status = result["status"]
            instr.applied_at = result["applied_at"]

            if result["status"] == "APPLIED":
                applied += 1
            else:
                failed += 1
                errors.append(result.get("error", "unknown"))

        if not dry_run:
            sess.status = SessionStatus.DONE if failed == 0 else SessionStatus.FAILED
            db.commit()

        return {"applied": applied, "failed": failed, "errors": errors}


    # ---------- PROGRESS ----------
    @staticmethod
    def get_progress(db: DBSession, sid) -> Optional[Dict]:
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None

        if sess.status not in {SessionStatus.APPLYING, SessionStatus.PLANNED}:
            # якщо не в процесі – 0 або 100 %
            percent = 100 if sess.status == SessionStatus.DONE else 0
            return {"percent": percent, "status": sess.status}

        total = sess.actions_total or 1
        done = db.query(FileInstruction).filter(
            FileInstruction.session_id == sid,
            FileInstruction.status != InstructionStatus.PENDING
        ).count()
        percent = int(done / total * 100)
        return {"percent": percent, "status": sess.status}
