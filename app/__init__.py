import os

from flask import Flask, render_template

from app.pages.routes import page_bp
from app.projects.routes import project_bp


def page_not_found(e):
    return render_template("errors/404.html"), 404


def internal_server_error(e):
    return render_template("errors/500.html"), 500


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs("project_data")
    except OSError:
        pass

    app.register_blueprint(page_bp)
    app.register_blueprint(project_bp)

    return app
