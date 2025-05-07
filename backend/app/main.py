import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import API_TITLE, API_DESCRIPTION, API_VERSION, API_PREFIX, DEBUG, FRONTEND_URL
from .api.routes import router as api_router
from .database import Base, engine

from .models import struct_session, file_descriptor, file_analysis, file_instruction

# Створення таблиць бази даних
Base.metadata.create_all(bind=engine)

# Створення додатку FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Додавання CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включення API маршрутів
app.include_router(api_router, prefix=API_PREFIX)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)