import logging
from functools import wraps
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram
import time
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

REQUEST_COUNT_2XX = Counter('request_count_2xx', 'Total 2xx HTTP requests')
REQUEST_COUNT_3XX = Counter('request_count_3xx', 'Total 3xx HTTP requests')
REQUEST_COUNT_4XX = Counter('request_count_4xx', 'Total 4xx HTTP requests')
REQUEST_COUNT_5XX = Counter('request_count_5xx', 'Total 5xx HTTP requests')

REQUEST_LATENCY = Histogram(
    name='request_latency_seconds',
    documentation='Time spent processing a request',
    buckets=(.1, .2, .3, .4, .5),
    labelnames=['endpoint']
)

TAILS_COUNTER = Counter('tails_counter', 'Tails counter')
HEADS_COUNTER = Counter('heads_counter', 'Heads counter')
FLIPS_COUNTER = Counter('flips_counter', 'Flips counter')


def measure_latency(log_message: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            start_time = time.time()
            response = await func(request, *args, **kwargs)
            latency = time.time() - start_time

            endpoint = request.url.path
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

            correlation_id = request.state.correlation_id
            logger.info(f"Correlation-ID: {correlation_id} | {log_message} | Endpoint: {endpoint} | Latency: {latency:.4f} seconds")

            return response

        return wrapper

    return decorator