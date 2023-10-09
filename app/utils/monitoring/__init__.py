# app/utils/monitoring/__init__.py
import os
from .sentry import configure_sentry
from .pyroscope import configure_pyroscope
from .logging import logger

def which_extras():
    # Check if SENTRY_DSN environment variable has a value
    if os.getenv("SENTRY_DSN"):
        configure_sentry()
        logger.info('Sentry Configured')

    # Check if PYROSCOPE_AUTH_TOKEN environment variable has a value
    if os.getenv("PYROSCOPE_AUTH_TOKEN"):
        configure_pyroscope()
        logger.info('Pyroscope Configured')

# Run It
if __name__ == "__main__":
    which_extras()
