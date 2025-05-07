from uuid import uuid4
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class SessionStatus(str, Enum):
    NEW = "NEW"
    ANALYZING = "ANALYZING"
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

    analysis_method = Column(String, nullable=True)      # META / STRUCT / SEMANTIC
    struct_algorithm = Column(String, nullable=True)     # BY_TYPE / CLUSTER / CRITERIA
    status = Column(String, default=SessionStatus.NEW)

    files_total = Column(Integer, default=0)
    actions_total = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    descriptors = relationship("FileDescriptor", back_populates="session", cascade="all, delete")
    analysis = relationship("FileAnalysis", back_populates="session", cascade="all, delete")
    instructions = relationship("FileInstruction", back_populates="session", cascade="all, delete")
