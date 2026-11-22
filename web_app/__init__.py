"""Create the Flask app used by the Flask CLI and the production server."""

import os
from secrets import token_hex

from flask import Flask, render_template

from web_app.routes.home_routes import home_routes
from web_app.routes.rps_routes import rps_routes
from web_app.routes.stocks_routes import stocks_routes


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY") or token_hex(32),
        SESSION_COOKIE_SECURE=os.getenv("RENDER") == "true",
    )

    app.register_blueprint(home_routes)
    app.register_blueprint(rps_routes)
    app.register_blueprint(stocks_routes)

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template("404.html"), 404

    return app
