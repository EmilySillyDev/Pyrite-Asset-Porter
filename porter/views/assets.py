from flask import Blueprint, render_template, current_app

import requests

bp = Blueprint('assets', __name__)

@bp.route('/assets/get-asset/<asset_id>')
def get_asset(asset_id):
    try:
        asset = current_app.config['USER'].get_asset(asset_id)
        return asset.name, 200
    except Exception as e:
        return str(e), 400

@bp.route('/assets/download-asset/<asset_id>')
def download_asset(asset_id):
    try:
        asset = current_app.config['USER'].get_asset_download(asset_id)
        request = requests.get(asset)
        if request.status_code == 200:
            return request.content, 200, {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename=asset_{asset_id}'
            }
        else:
            raise Exception(f"Failed to download asset: {request.status_code} - {request.text}")
        
    except Exception as e:
        return str(e), 400