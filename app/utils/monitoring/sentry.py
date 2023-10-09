# app/utils/monitoring/sentry.py
import os
from .logging import logger, LOG_LEVEL
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration


def configure_sentry():
    """Configure Sentry with custom sampling logic."""
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            LoggingIntegration(level=LOG_LEVEL),
            ExcepthookIntegration(always_run=True),
            ModulesIntegration(),
            ThreadingIntegration(propagate_hub=True),
        ],
        traces_sample_rate=traces_sampler(),
        profiles_sample_rate=profiles_sampler(),
    )


def traces_sampler(sampling_context=None):
    """Customize trace sampling logic if needed.

    Args:
        sampling_context (dict, optional): Context for the sampling decision.

    Returns:
        float: Sampling rate between 0 and 1.
    """
    default_sampling_rate = 1.0

    if sampling_context is None:
        sampling_rate = default_sampling_rate
    elif sampling_context.get("food") == "Tacos":
        sampling_rate = 0.5
    elif sampling_context.get("food") == "Pears":
        sampling_rate = 0.5
    else:
        sampling_rate = default_sampling_rate

    logger.info(f'Traces Sampling Rate: %s', sampling_rate)
    return sampling_rate


def profiles_sampler(sampling_context=None):
    """Customize profile sampling logic if needed.

    Args:
        sampling_context (dict, optional): Context for the sampling decision.

    Returns:
        float: Sampling rate between 0 and 1.
     """
    default_sampling_rate = 1.0

    if sampling_context is None:
        sampling_rate = default_sampling_rate
    elif sampling_context.get("food") == "Tacos":
        sampling_rate = 0.5
    elif sampling_context.get("food") == "Pears":
        sampling_rate = 0.5
    else:
        sampling_rate = default_sampling_rate

    logger.info(f'Profile Sampling Rate: %s', sampling_rate)
    return sampling_rate


# Test
if __name__ == "__main__":
    try:
        division_by_zero = 1 / 0
    except ZeroDivisionError:
        sentry_sdk.capture_exception()
