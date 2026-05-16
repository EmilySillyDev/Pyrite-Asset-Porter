from flask import Blueprint, render_template, current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html.j2')

@bp.route('/debug')
def debug():
    return render_template('debug.html.j2')
