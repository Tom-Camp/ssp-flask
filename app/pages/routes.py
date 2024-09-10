from flask import Blueprint, render_template

from app.utils.helpers import load_yaml


def get_content(page: str):
    content = load_yaml("app/pages/content.yaml")
    return content.get(page, "")


page_bp = Blueprint("pages", __name__)


@page_bp.route("/", methods=["GET"])
def index():
    page_data = {
        "intro": get_content("index"),
    }
    return render_template("page/index.html", **page_data)


@page_bp.route("/resources", methods=["GET"])
def resources():
    page_data = {
        "content": get_content("resources"),
    }
    return render_template("docs/resources.html", **page_data)
