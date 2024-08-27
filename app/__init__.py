import logging.config
import os

from flask import Flask, render_template

from app.pages.routes import page_bp
from app.projects.routes import project_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    logging.config.fileConfig("app/logging.conf")

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

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"An error occurred: {e}")
        return render_template("errors/500.html"), 500

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.error(f"404 error: {error}")
        return render_template("errors/404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
