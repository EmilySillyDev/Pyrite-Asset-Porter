from flask import Blueprint, render_template, current_app

bp = Blueprint('history', __name__)

@bp.route('/history')
def history():
    return render_template('index.html.j2')