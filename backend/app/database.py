from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

# 1. Оголошуємо Base одразу
Base = declarative_base()

# 2. Створюємо engine та фабрику сесій
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}    # для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Залежність для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
