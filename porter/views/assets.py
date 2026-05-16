from flask import Blueprint, render_template, current_app

bp = Blueprint('assets', __name__)

@bp.route('/assets/get-asset/<asset_id>')
def get_asset(asset_id):
    try:
        asset = current_app.config['USER'].get_asset(asset_id)
        return asset
    except Exception as e:
        return str(e), 400

@bp.route('/assets/download-asset/<asset_id>')
def download_asset(asset_id):
    try:
        asset = current_app.config['USER'].get_asset(asset_id)
        print(asset)
        return "WIP"
    except Exception as e:
        return str(e), 400