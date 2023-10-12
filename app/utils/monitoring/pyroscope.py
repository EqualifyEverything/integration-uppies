# app/utils/monitoring/pyroscope.py
import os
import socket
import platform
from .logging import logger
import pyroscope

def configure_pyroscope():
    logger.info('Configuring Pyroscope')
    host = socket.gethostname()
    platform_info = platform.platform()
    python_version = platform.python_version()
    host_os = platform.system()
    host_os_release = platform.release()
    host_os_version = platform.version()
    host_machine_type = platform.machine()
    host_processor = platform.processor()
    python_implementation = platform.python_implementation()
    python_compiler = platform.python_compiler()
    python_build = platform.python_build()
    logger.debug('Pyroscope Vars Imported...')

    pyroscope.configure(
        application_name=os.getenv("PYROSCOPE_APPLICATION_NAME"),
        server_address=os.getenv("PYROSCOPE_SERVER"),
        auth_token=os.getenv("PYROSCOPE_API_KEY"),
    )
    logger.info('Pyroscope Configured')


def traces_sampler(sampling_context):
    # Customize your sampling logic here if needed
    # return a number between 0 and 1 or a boolean
    return 1.0

