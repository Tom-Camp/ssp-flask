import os

from flask import Flask, render_template

from app.projects.routes import project_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs("project_data")
    except OSError:
        pass

    app.register_blueprint(project_bp)

    @app.route("/")
    def hello():
        return render_template("index.html")

    return app
