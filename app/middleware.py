import uuid
from app.metrics import REQUEST_COUNT_2XX, REQUEST_COUNT_4XX, REQUEST_COUNT_5XX
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request

class RequestCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        if 200 <= response.status_code < 300:
            REQUEST_COUNT_2XX.inc()  # Используем уже зарегистрированную метрику
        elif 400 <= response.status_code < 500:
            REQUEST_COUNT_4XX.inc()
        elif 500 <= response.status_code < 600:
            REQUEST_COUNT_5XX.inc()
        return response

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers['X-Correlation-ID'] = correlation_id
        return response