import os

from flask import Flask
from .views import main

def create_app():
    app = Flask(__name__)
    key = os.urandom(16)

    app.jinja_env.add_extension('jinja2.ext.do')
    app.secret_key = "DEBUG_KEY" if app.debug else key

    # Register blueprints
    app.register_blueprint(main.bp)

    return app