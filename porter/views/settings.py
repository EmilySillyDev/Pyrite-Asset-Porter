from flask import Blueprint, render_template, current_app, request

bp = Blueprint('settings', __name__)

@bp.route('/settings')
def settings():
    return render_template('settings.html.j2')

@bp.route('/settings/save-settings', methods=['POST'])
def save_settings():
    current_app.config['USER'].save()
    return "Settings saved successfully", 200

@bp.route('/settings/save-login', methods=['POST'])
def save_login():
    data = request.get_json(silent=True)
    if data:
        user_id = data.get('user_id')
        api_key = data.get('api_key')
    else:
        user_id = request.form.get('user_id')
        api_key = request.form.get('api_key')

    if user_id:
        current_app.config['USER'].set_user_id(user_id)
    if api_key:
        current_app.config['USER'].set_api_key(api_key)

    current_app.config['USER'].save()
    return "Login information saved successfully", 200

@bp.route('/settings/set-api-key', methods=['POST'])
def set_api_key():
    data = request.get_json(silent=True)
    if data:
        api_key = data.get('api_key')
    else:
        api_key = request.form.get('api_key')

    if api_key:
        current_app.config['USER'].set_api_key(api_key)
        return "API key set successfully", 200
    else:
        return "Missing API key", 400

@bp.route('/settings/add-group', methods=['POST'])
def add_group():
    data = request.get_json(silent=True)
    if data:
        group_name = data.get('group_name')
        group_id = data.get('group_id')
    else:
        group_name = request.form.get('group_name')
        group_id = request.form.get('group_id')

    print(f"Received group name: {group_name}, group ID: {group_id}")
    group_id = int(group_id) if group_id else None

    if group_name and group_id:
        current_app.config['USER'].add_group(group_name, group_id)
        return "Group added successfully", 200
    else:
        return "Missing group name or ID (is your ID numerical?)", 400
    
@bp.route('/settings/get-groups')
def get_groups():
    groups = current_app.config['USER'].get_groups()
    return {"groups": groups}, 200

@bp.route('/settings/set-target-group', methods=['POST'])
def set_target_group():
    data = request.get_json(silent=True)
    if data:
        target_group = data.get('target_group')
    else:
        target_group = request.form.get('target_group')

    print(f"Received target group: {target_group}")

    if target_group:
        current_app.config['USER'].set_target_group(target_group)
        return "Target group set successfully", 200
    else:
        current_app.config['USER'].set_target_group(None)
        return "Cleared target group", 200

@bp.route('/settings/remove-group', methods=['POST'])
def remove_group():
    data = request.get_json(silent=True)
    if data:
        group_id = data.get('group_id')
    else:
        group_id = request.form.get('group_id')

    if group_id:
        current_app.config['USER'].remove_group(group_id)

        return "Group removed successfully", 200
    else:
        return "Missing group ID", 400