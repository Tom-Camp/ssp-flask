import os

from flask import Flask, render_template

from app.projects.routes import project_bp
from app.utils.helpers import get_projects


def intro_text():
    return """
    The SSP Toolkit is used to create System Security Plans using components
    and templates. Components, appendices, and frontmatter can be added to a
    project and edited. Key YAML files containing variables that can be used
    to populate the variables in the templates can be edited and created.

    You can create a Project here or clone a git repository of Project files
    in the project_data directory. Any directory in the project_directory that
    includes a project.yaml file will be accessible in the Toolkit.
    """


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
    def index():
        projects = get_projects()
        page_data = {
            "projects": projects if len(projects) <= 5 else projects[:5],
            "intro": intro_text(),
        }
        return render_template("page/index.html", **page_data)

    return app
