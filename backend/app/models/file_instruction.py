from uuid import uuid4
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class ActionType(str, Enum):
    CREATE_DIR = "CREATE_DIR"
    DELETE_EMPTY_DIR = "DELETE_EMPTY_DIR"
    MOVE_FILE = "MOVE_FILE"
    RENAME_FILE = "RENAME_FILE"


class InstructionStatus(str, Enum):
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    FAILED = "FAILED"


class FileInstruction(Base):
    __tablename__ = "file_instructions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("struct_sessions.id", ondelete="CASCADE"))
    file_hash = Column(String, index=True)

    action = Column(String, nullable=False)        # ActionType
    status = Column(String, default=InstructionStatus.PENDING)
    params = Column(JSON, default={})

    applied_at = Column(DateTime, nullable=True)

    # back‑ref
    session = relationship("StructSession", back_populates="instructions")
