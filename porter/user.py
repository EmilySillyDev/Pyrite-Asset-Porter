#   Rough Concept, wip
#
#   isAuthenticated() -> bool
#   currentApiKey() -> Optional[str]
#   storedApiKeys() -> List[str]
#   addApiKey(key: str) -> None
#   removeApiKey(key: str) -> None
#

import configparser
import json
import os
import time

from dataclasses import dataclass

import requests

from appdata import AppDataPaths
from rblxopencloud import ApiKey
from rblxopencloud import User as RobloxUser

@dataclass
class HistoryEntry:
    name: str
    asset_id: int
    timestamp: float | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class User:
    def __init__(self):
        app_paths = AppDataPaths("Pyrite Asset Porter")
        app_paths.setup()

        self.paths = app_paths

        self.current_api_key = None
        self.user_id = None
        self.target_group = None

        self.user = None
        self.groups = []
        self.session_history = []

        self.load_data()

    def get_asset_delivery_info(self, asset_id):
        if not self.is_authenticated():
            raise Exception("User is not authenticated")
        
        # https://apis.roblox.com/asset-delivery-api/v1/assetId/{assetId}
        link = f"https://apis.roblox.com/asset-delivery-api/v1/assetId/{asset_id}"
        headers = {
            "x-api-key": f"{self.current_api_key}"
        }
        
        request = requests.get(link, headers=headers)

        if request.status_code == 200:
            return request.json()
        else:
            raise Exception(f"Failed to fetch asset delivery info: {request.status_code} - {request.text}")


    def load_data(self):
        config_file = self.paths.config_path

        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)

            selected_key = config.get('API', 'current_api_key', fallback=None)
            self.current_api_key = selected_key

            self.target_group = config.get('GROUP', 'target_group', fallback=None)

            if self.target_group == "":
                self.target_group = None

            if self.target_group is not None:
                self.target_group = int(self.target_group)

            self.user_id = config.get('API', 'user_id', fallback=None)

            if self.user_id == "":
                self.user_id = None

            if self.user_id is not None:
                self.user_id = int(self.user_id)

            # if (self.current_api_key is not None) and (self.user_id is not None):
            self.setup_user()

        self.groups = self.load_groups()

    def get_user_id(self):
        return self.user_id if hasattr(self, 'user_id') else None
    
    def set_user_id(self, user_id):
        self.user_id = user_id
        self.setup_user()
        self.save()
    
    def get_asset_download(self, asset_id):
        info = self.get_asset_delivery_info(asset_id)
        if 'location' in info:
            return info['location']
        else:
            raise Exception("Asset delivery info does not contain a download location")

    def save(self):
        data_path = self.paths.app_data_path

        with open(os.path.join(data_path, 'groups.json'), 'w') as f:
            json.dump(self.groups, f, indent=4)

        config_file = self.paths.config_path
        config = configparser.ConfigParser()

        config['API'] = {}
        if self.current_api_key is not None:
            config['API']['current_api_key'] = self.current_api_key

        if self.user_id is not None:
            config['API']['user_id'] = str(self.user_id)

        config['GROUP'] = {}
        if self.target_group is not None:
            config['GROUP']['target_group'] = str(self.target_group)

        with open(config_file, 'w') as f:
            config.write(f)

    def load_groups(self):
        groups_file = os.path.join(self.paths.app_data_path, 'groups.json')

        if os.path.exists(groups_file):
            with open(groups_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        else:
            return []
        
    def add_group(self, group_name, group_id):
        if type(group_id) != int:
            raise ValueError("Group ID must be an integer")
        
        if not any(group['id'] == group_id for group in self.groups):
            self.groups.append({'name': group_name, 'id': group_id})
            self.save()

    def remove_group(self, group_id):
        if type(group_id) != int:
            raise ValueError("Group ID must be an integer")

        self.groups = [group for group in self.groups if group['id'] != group_id]

        if self.target_group == group_id:
            self.target_group = None

        self.save()

    def get_groups(self):
        return self.groups

    def set_target_group(self, target_group):
        if target_group is None:
            self.target_group = None
            self.save()
            return

        if not any(group['id'] == target_group for group in self.groups):
            raise ValueError(f"Group '{target_group}' does not exist")

        self.target_group = int(target_group)
        self.save()

    def get_target_group_name(self):
        if self.target_group is None:
            return None

        for group in self.groups:
            if group['id'] == self.target_group:
                return group['name']
        
        return None
    
    def set_api_key(self, api_key):
        self.current_api_key = api_key
        self.setup_user()
        self.save()

    def setup_user(self):
        if (self.current_api_key is not None) and (self.user_id is not None):
            try:
                self.user = RobloxUser(self.user_id, self.current_api_key)
            except Exception as e:
                print(f"Failed to validate API key: {e}")
                self.current_api_key = None
                self.rblx_api = None
                self.user = None

    def get_roblox_api(self):
        if not self.is_authenticated():
            raise Exception("User is not authenticated")
        
        return self.user

    def is_authenticated(self):
        return self.user is not None
    
    def open_app_data(self):
        path = self.paths.app_data_path
        if os.path.exists(path):
            os.startfile(path)