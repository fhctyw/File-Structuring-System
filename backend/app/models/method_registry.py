from enum import Enum

from sqlalchemy import Column, String, Boolean, JSON, Enum as PgEnum
from ..database import Base


class MethodsLayer(str, Enum):
    META = "META"
    STRUCT = "STRUCT"
    CONTENT = "CONTENT"


class MethodRegistry(Base):
    __tablename__ = "methods"

    id = Column(String, primary_key=True)
    layer = Column(PgEnum(MethodsLayer), nullable=False)
    domain = Column(String, nullable=False)
    action = Column(String, nullable=False)
    description = Column(String, nullable=True)

    returns = Column(JSON, default=list)

    impl_class = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
