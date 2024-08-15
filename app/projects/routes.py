from flask import Blueprint, render_template, request

project_bp = Blueprint("project", __name__, url_prefix="/project")


@project_bp.route("/list", methods=["GET"])
def projects_list():
    return render_template("project/projects.html")


@project_bp.route("/create", methods=["GET", "POST"])
def projects_create():
    if request.method == "GET":
        """"""
    elif request.method == "POST":
        """"""
