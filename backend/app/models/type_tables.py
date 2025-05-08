from uuid import uuid4

from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base


class FileType(Base):
    """
    Користувацька/адмінська таблиця: визначає,
    які STRUCT/CONTENT-модулі застосувати до MIME-типу.
    """
    __tablename__ = "file_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    mime_type = Column(String, unique=True, nullable=False)       # "image/jpeg"
    extensions = Column(JSON, nullable=False, default=list)       # ["jpg", "jpeg"]
    category = Column(String, nullable=False)                     # "image"

    struct_methods = Column(JSON, nullable=False, default=list)   # ["IMAGE_RESOLUTION", ...]
    content_methods = Column(JSON, nullable=False, default=list)  # ["IMAGE_OBJECTS", ...]

    enabled = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
