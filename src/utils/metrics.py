from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUESTS = Counter('requests_total', 'Total number of requests')
LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')
JUMP_COUNTER = Counter(
    'jump_total', 'Total number of URLs processed by Uppies')

JUMP_LATENCY = Histogram(
    'jump_latency_seconds', 'URL processing latency for Uppies')

ACTIVE_THREADS = Gauge('active_threads', 'Number of active threads in Uppies')
ERRORS = Counter('errors_total', 'Total number of errors encountered')
RETRIES = Counter('retries_total', 'Total number of URL retries')
QUEUE_SIZE = Gauge('queue_size', 'Number of URLs in the RabbitMQ queue')


SUCCESS_COUNT = Counter(
    'jump_success_total',
    'Total number of URLs successfully tested',
    labelnames=['endpoint'])

FAILURE_COUNT = Counter(
    'jump_failure_total',
    'Total number of URLs that failed testing',
    labelnames=['endpoint'])