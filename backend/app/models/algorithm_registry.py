from sqlalchemy import Column, String, Boolean, JSON
from ..database import Base


class AlgorithmRegistry(Base):
    """
    Системна таблиця: перелік усіх алгоритмів структурування.
    У UI користувач бачить лише id, description і форму, зібрану з params_schema.
    """
    __tablename__ = "struct_algorithms"

    id = Column(String, primary_key=True)        # "CRITERIA", "CLUSTER", ...
    description = Column(String, nullable=True)

    params_schema = Column(JSON, default=dict)

    # "*" або список категорій / MIME-типів, якщо алгоритм має обмеження
    scope = Column(JSON, default="*")

    impl_class = Column(String, nullable=False)

    enabled = Column(Boolean, default=True)