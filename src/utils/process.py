import os
import requests
from utils.watch import logger
from data.insert import record_uppies


def uppies(url, url_id):
    # Check if environment variables are present
    http_proxy = os.environ.get('http_proxy', 'http://192.168.1.15:18888')
    https_proxy = os.environ.get('https_proxy', 'http://192.168.1.15:18888')

    # Set proxies if environment variables are present
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy

    logger.debug(f'Processing: {url}')
    try:
        response = requests.head(url, timeout=5, proxies=proxies)
        data = {
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'response_time': response.elapsed.total_seconds(),
            'charset': response.encoding,
            'page_last_modified': response.headers.get('Last-Modified', ''),
            'content_length': response.headers.get('Content-Length', ''),
            'server': response.headers.get('Server', ''),
            'x_powered_by': response.headers.get('X-Powered-By', ''),
            'x_content_type_options': response.headers.get('X-Content-Type-Options', ''),
            'x_frame_options': response.headers.get('X-Frame-Options', ''),
            'x_xss_protection': response.headers.get('X-XSS-Protection', ''),
            'content_security_policy': response.headers.get('Content-Security-Policy', ''),
            'strict_transport_security': response.headers.get('Strict-Transport-Security', ''),
            'etag': response.headers.get('ETag', '')
        }
        record_uppies((url_id, data))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {url} - {str(e)}")
        record_uppies((url_id, {
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
        }))
    except UnicodeError as e:
        logger.error(f"Encoding error with URL: {url} - {str(e)}")
        record_uppies((url_id, {
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
        }))

