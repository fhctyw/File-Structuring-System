from uuid import uuid4
from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class SessionStatus(str, Enum):
    NEW = "NEW"
    ANALYZED = "ANALYZED"
    PLANNED = "PLANNED"
    APPLYING = "APPLYING"
    DONE = "DONE"
    FAILED = "FAILED"


class StructSession(Base):
    __tablename__ = "struct_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    directory = Column(String, nullable=False)
    recursive = Column(Boolean, default=True)

    analysis_method_id  = Column(
        String,
        ForeignKey("methods.id", ondelete="SET NULL"),
        nullable=True
    )                                    # META / STRUCT / CONTENT  → MethodRegistry.id

    struct_algorithm_id = Column(
        String,
        ForeignKey("struct_algorithms.id", ondelete="SET NULL"),
        nullable=True
    )                                    # CRITERIA / CLUSTER ...   → AlgorithmRegistry.id
    
    status = Column(String, default=SessionStatus.NEW)

    files_total = Column(Integer, default=0)
    actions_total = Column(Integer, default=0)

    # relationships
    instructions = relationship("FileInstruction", back_populates="session", cascade="all, delete")
