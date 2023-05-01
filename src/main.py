import os
import threading
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from utils.watch import logger
from utils.process import jump, bad_jump
import importlib
from utils.auth import catch_rabbits
from utils.metrics import (
                            REQUESTS, LATENCY, JUMP_COUNTER,
                            JUMP_LATENCY, ACTIVE_THREADS,
                            ERRORS, RETRIES, QUEUE_SIZE,
                            SUCCESS_COUNT, FAILURE_COUNT)
from prometheus_client import generate_latest
from functools import wraps
import time


app = Flask(__name__)
CORS(app)


# Endpoints
@app.route('/yeet', methods=['POST'])
def process_urls():
    data = request.json
    threads = []
    for item in data:
        url = item['url']
        url_id = item['url_id']
        thread = threading.Thread(target=jump, args=(url, url_id))
        thread.start()
        threads.append(thread)
        ACTIVE_THREADS.inc()

    for thread in threads:
        thread.join()
        ACTIVE_THREADS.dec()

    return jsonify({"message": "Processing completed"}), 200


def consume_urls():
    """
    Description:
        Consumes URLs from a RabbitMQ queue and processes them with uppies

    Raises:
        Any exceptions raised by the uppies function.
    """
    queue_name = 'launch_uppies'
    while True:
        try:
            def callback(ch, method, properties, body):
                message = json.loads(body.decode('utf-8'))
                url = message.get('url')
                url_id = message.get('url_id')
                with ThreadPoolExecutor(max_workers=10) as executor:
                    try:
                        future = executor.submit(jump, url, url_id)
                        # Set a timeout of 15 seconds
                        future.result(timeout=15)
                    except TimeoutError:
                        logger.error(
                            f'❌ Timeout reached while processing URL: {url}')
                        data = 'Timeout Error'
                        bad_jump(url_id, data)

                        ch.basic_nack(method.delivery_tag)

            # Consume URLs from the RabbitMQ queue
            catch_rabbits(queue_name, callback)
        except Exception as e:
            # Log any errors that occur while consuming URLs from the queue
            logger.error(f'Error in consume_urls: {e}')
            # Wait 5 seconds before trying again
            time.sleep(5)


def measure_latency(endpoint):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start_time = time()
            response = func(*args, **kwargs)
            LATENCY.labels(endpoint=endpoint).observe(time() - start_time)
            REQUESTS.labels(endpoint=endpoint).inc()
            return response
        return wrapped
    return decorator


@app.route('/health')
@measure_latency('/health')
def get_health():
    logger.debug('Health Check Requested')
    health = "ok"

    return jsonify({"status": health}), 200


@app.route('/metrics')
@measure_latency('/metrics')
def metrics():
    main = importlib.import_module("main")
    JUMP_COUNTER = main.JUMP_COUNTER
    JUMP_LATENCY = main.JUMP_LATENCY
    SUCCESS_COUNT = main.SUCCESS_COUNT
    FAILURE_COUNT = main.FAILURE_COUNT
    start_time = time()
    # Collect and return the metrics as a Prometheus-formatted response
    response = Response(generate_latest(), mimetype='text/plain')
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


# Start the Flask app and consume URLs in a separate thread
if __name__ == '__main__':
    # Get the port number from the environment variable or use 8083 as default
    app_port = int(os.environ.get('APP_PORT', 8085))

    # Start consume_urls in a separate thread
    consume_thread = threading.Thread(target=consume_urls, daemon=True)
    consume_thread.start()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=app_port)