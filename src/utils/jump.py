import os
import requests
import json
from time import time
from utils.watch import logger
from utils.auth import rabbit
from utils.metrics import (
    JUMP_COUNTER, JUMP_LATENCY,
    SUCCESS_COUNT, FAILURE_COUNT)


# Queue to get urls to test: am_i_up
# Queue for recording good urls: i_am_up
# queue for bad urls: i_am_down


def jump(url, url_id):
    logger.debug(f'Starting to JUMP: {url}')
    start_time = time()
    # Set the proxy settings using environment variables
    proxies = {}
    use_proxy = os.environ.get('USE_PROXY', 'true').lower() == 'true'
    proxy_http = os.environ.get('PROXY_HTTP', '192.168.1.56:8888')
    proxy_https = os.environ.get('PROXY_HTTPS', '192.168.1.56:8888')
    if use_proxy:
        if proxy_http:
            proxies['http'] = proxy_http
        if proxy_https:
            proxies['https'] = proxy_https

    # Test URL
    logger.debug(f'Processing: {url}')
    try:
        response = requests.head(url, timeout=5, proxies=proxies)
        logger.debug(f'URL: {url} - Status code: {response.status_code}, Content-Type: {response.headers.get("Content-Type", "")}, Response time: {response.elapsed.total_seconds()}')
        data = {
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'response_time': response.elapsed.total_seconds(),
            'charset': response.encoding,
            'page_last_modified': response.headers.get('Last-Modified', ''),
            'content_length': response.headers.get('Content-Length', ''),
            'server': response.headers.get('Server', ''),
            'x_powered_by': response.headers.get('X-Powered-By', ''),
            'x_content_type_options':
                response.headers.get('X-Content-Type-Options', ''),

            'x_frame_options': response.headers.get('X-Frame-Options', ''),
            'x_xss_protection': response.headers.get('X-XSS-Protection', ''),
            'content_security_policy':
            response.headers.get('Content-Security-Policy', ''),

            'strict_transport_security':
            response.headers.get('Strict-Transport-Security', ''),

            'etag': response.headers.get('ETag', '')
        }
        # Replaced record_uppies with good_jump
        good_jump(url_id, data)
        SUCCESS_COUNT.labels(endpoint='/jump').inc()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {url} - {str(e)}")
        logger.debug(f"URL: {url} - Error details: {str(e)}")
        # Replaced record_uppies with bad_jump
        bad_jump(url_id, {
            'status_code': 999,
            'content_type': '',
            'response_time': 0,
            'charset': '',
            'page_last_modified': '',
            'content_length': '',
            'server': '',
            'x_powered_by': '',
            'x_content_type_options': '',
            'x_frame_options': '',
            'x_xss_protection': '',
            'content_security_policy': '',
            'strict_transport_security': '',
            'etag': ''
        })
    except UnicodeError as e:
        logger.error(f"Encoding error with URL: {url} - {str(e)}")
        logger.debug(f"URL: {url} - Error details: {str(e)}")
        # Replaced record_uppies with bad_jump
        bad_jump(url_id, {
            'status_code': 998,
            'content_type': '',
            'response_time': 0,
            'charset': '',
            'page_last_modified': '',
            'content_length': '',
            'server': '',
            'x_powered_by': '',
            'x_content_type_options': '',
            'x_frame_options': '',
            'x_xss_protection': '',
            'content_security_policy': '',
            'strict_transport_security': '',
            'etag': ''
        })
        FAILURE_COUNT.labels(endpoint='/jump').inc()

    JUMP_COUNTER.inc()
    JUMP_LATENCY.observe(time() - start_time)


def good_jump(url_id, data):
    message = json.dumps({"url_id": url_id, "data": data})
    logger.debug(
        f'Sending good_jump message for URL ID: {url_id} - Data: {data}')
    rabbit('i_am_up', message)


def bad_jump(url_id, data):
    message = json.dumps({"url_id": url_id, "data": data})
    logger.debug(
        f'Sending bad_jump message for URL ID: {url_id} - Data: {data}')
    rabbit('i_am_down', message)
