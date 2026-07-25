import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """
    Base configuration shared by the entire application.
    """

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "temporary-development-secret-key",
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'phishguard.db'}",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024