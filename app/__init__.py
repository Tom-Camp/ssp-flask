import os

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from app.logging_config import loguru_logger as logger
from app.pages.routes import page_bp
from app.projects.opencontrol_routes import opencontrol_bp
from app.projects.routes import project_bp


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

    app.register_blueprint(page_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(opencontrol_bp)

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        logger.exception(f"Exception: {e}")
        return render_template("errors/500.html", error=e.description), 500

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    return app
