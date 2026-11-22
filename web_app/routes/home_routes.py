"""Basic GET routes from the class routing exercise."""

from flask import Blueprint, render_template, request

home_routes = Blueprint("home_routes", __name__)


@home_routes.get("/home")
@home_routes.get("/")
def index():
    return render_template("home.html")


@home_routes.get("/about")
def about():
    return render_template("about.html")


@home_routes.get("/hello")
def hello_world():
    name = request.args.get("name", "").strip() or "World"
    return render_template("hello.html", message=f"Hello, {name}!")
