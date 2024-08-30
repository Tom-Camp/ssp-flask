import logging
import os

from flask import Flask, render_template
from loguru import logger

from app.components.routes import component_bp
from app.pages.routes import page_bp
from app.projects.routes import project_bp


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    if config_name:
        app.config.from_object(config_name)
    else:
        app.config.from_object("config.DevelopmentConfig")

    try:
        os.makedirs("project_data")
    except OSError:
        pass

    logger.start(
        app.config["LOGFILE"],
        level=app.config["LOG_LEVEL"],
        format="{time} {level} {message}",
        backtrace=app.config["LOG_BACKTRACE"],
        rotation="25 MB",
    )
    app.logger.addHandler(InterceptHandler())

    app.register_blueprint(component_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(project_bp)

    @app.errorhandler(Exception)
    def handle_exception(e):
        return render_template("errors/500.html", error=e), 500

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    return app
