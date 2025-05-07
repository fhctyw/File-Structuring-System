from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class FileAnalysis(Base):
    __tablename__ = "file_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("struct_sessions.id", ondelete="CASCADE"))
    file_hash = Column(String, index=True)

    description = Column(String, nullable=False)

    # back‑ref
    session = relationship("StructSession", back_populates="analysis")
