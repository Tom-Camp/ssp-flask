import os
from pathlib import Path

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    ROOT_DIR = Path(__file__).parent.resolve()

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    LOG_BACKTRACE = True


class ProductionConfig(Config):
    LOG_BACKTRACE = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
