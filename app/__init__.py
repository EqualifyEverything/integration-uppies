# app/__init__.py
from .utils import configure_monitoring
from dotenv import load_dotenv


def startup():
    load_dotenv()
    configure_monitoring()
