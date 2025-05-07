from uuid import uuid4
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class FileDescriptor(Base):
    __tablename__ = "file_descriptors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("struct_sessions.id", ondelete="CASCADE"))

    file_hash = Column(String, index=True)
    filename = Column(String)
    original_path = Column(String)
    file_type = Column(String)
    mime_type = Column(String)
    size_bytes = Column(Integer)

    # back‑ref
    session = relationship("StructSession", back_populates="descriptors")
