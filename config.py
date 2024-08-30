import os
from pathlib import Path

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    ROOT_DIR = Path(__file__).parent.resolve()
    LOGFILE = ROOT_DIR.joinpath("instance").joinpath("logger").with_suffix(".log")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_BACKTRACE = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    LOG_BACKTRACE = False
    LOG_LEVEL = "INFO"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
