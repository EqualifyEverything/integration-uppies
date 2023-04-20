import os
from utils.watch import logger, test_database
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.process import uppies

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
        thread = threading.Thread(target=uppies, args=(url, url_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return jsonify({"message": "Processing completed"}), 200


@app.route('/health')
def get_health():
    logger.debug('Health Check Requested')
    health = "ok"

    if not test_database():
        health = "error: Database Connection"

    return jsonify({"status": health}), 200


if __name__ == '__main__':
    app_port = int(os.environ.get('APP_PORT', 8085))
    app.run(debug=True, host='0.0.0.0', port=app_port)
