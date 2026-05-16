import os

from appdata import AppDataPaths
from flask import Flask

from .views import main, settings
from . import user

current_user = None

def create_app():
    app = Flask(__name__)
    key = os.urandom(16)

    current_user = user.User()
    app.config['USER'] = current_user

    app.jinja_env.add_extension('jinja2.ext.do')
    app.secret_key = "DEBUG_KEY" if app.debug else key

    # Register blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(settings.bp)

    return app