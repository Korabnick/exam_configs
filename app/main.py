from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from app.middleware import RequestCountMiddleware, CorrelationIDMiddleware
from app.metrics import REQUEST_COUNT_2XX, REQUEST_COUNT_3XX, REQUEST_COUNT_4XX, REQUEST_COUNT_5XX, measure_latency
from app.model.meta import Base
from config.settings import settings
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Инициализация приложения
app = FastAPI()

# Добавляем middleware
app.add_middleware(CorrelationIDMiddleware)  # для обработки Correlation-ID
app.add_middleware(RequestCountMiddleware)   # для подсчёта запросов

# Настройка базы данных (если нужно)
SQLALCHEMY_DATABASE_URL = settings.db_url
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Пример роутинга
@app.get("/tech/healthcheck")
@measure_latency("Healthcheck endpoint")
async def healthcheck(request: Request):
    return {"status": "ok"}

@app.get("/tech/metrics")
@measure_latency("Metrics endpoint")
async def metrics(request: Request):
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Основной запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
