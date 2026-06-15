from flask import Blueprint, render_template, current_app, request
import requests

from io import BytesIO
from rblxopencloud import AssetType, Asset, Group
from porter.user import HistoryEntry

bp = Blueprint('assets', __name__)

# requires auth decorator
def requires_auth(f):
    def decorated_function(*args, **kwargs):
        if not current_app.config['USER'].is_authenticated():
            return "User is not authenticated", 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/assets/get-asset/<asset_id>')
@requires_auth
def get_asset(asset_id):
    try:
        asset = current_app.config['USER'].get_asset(asset_id)
        return asset.name, 200
    except Exception as e:
        return str(e), 400

@bp.route('/assets/download-asset/<asset_id>')
@requires_auth
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
    
@bp.route('/assets/reupload-asset/<asset_id>', methods=['POST'])
@requires_auth
def reupload_asset(asset_id):
    # get asset name, type, and content
    # then upload

    try:
        delivery_info = current_app.config['USER'].get_asset_delivery_info(asset_id)
        if 'location' not in delivery_info:
            return "Asset delivery info does not contain a download location", 400
        
        download_url = delivery_info['location']
        download_request = requests.get(download_url)

        if download_request.status_code != 200:
            raise Exception(f"Failed to download asset: {download_request.status_code} - {download_request.text}")
        
        asset_content_raw = download_request.content
        asset_content = BytesIO(asset_content_raw)
        asset_content.name = f"asset_{asset_id}.rbxm"  # or .rbxmx depending on the asset type

        user = current_app.config['USER']

        if not user.is_authenticated():
            return "User is not authenticated", 401
        
        if not user.target_group:
            return "Target group is not set. Please set a target group in settings.", 400

        userCreator = user.get_roblox_api()
        groupCreator = Group(user.target_group, user.current_api_key)

        asset = userCreator.fetch_asset(asset_id)

        data = request.get_json(silent=True)
        user_given_name = None
        if data:
            user_given_name = data.get('name', None)

        new_asset = groupCreator.upload_asset(
            asset_content,
            AssetType.Animation,
            name=user_given_name or asset.name,
            description=f"Re-uploaded from asset {asset_id}"
        )

        final_asset = None

        if isinstance(new_asset, Asset):
            final_asset = new_asset
        else:
            status = new_asset.wait()
            final_asset = status

        # Add to history
        history_entry = HistoryEntry(name=final_asset.name, asset_id=final_asset.id)
        user.session_history.append(history_entry)

        return {"new_asset_id": final_asset.id}, 200
        # return f"Asset re-uploaded successfully. New Asset ID: {final_asset.id}", 200
    except Exception as e:
        print(f"Error re-uploading asset: {e}")
        return str(e), 400