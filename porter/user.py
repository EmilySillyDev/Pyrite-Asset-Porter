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

from appdata import AppDataPaths

class User:
    def __init__(self):
        app_paths = AppDataPaths("Pyrite Asset Porter")
        app_paths.setup()

        self.paths = app_paths

        self.current_api_key = None
        self.target_group = None
        self.groups = []

        self.load_data()
    
    def load_data(self):
        config_file = self.paths.config_path

        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)

            selected_key = config.get('API', 'current_api_key', fallback=None)
            self.current_api_key = selected_key
            self.target_group = config.get('GROUP', 'target_group', fallback=None)

        self.groups = self.load_groups()

    def save(self):
        data_path = self.paths.app_data_path

        with open(os.path.join(data_path, 'groups.json'), 'w') as f:
            json.dump(self.groups, f, indent=4)

        config_file = self.paths.config_path
        config = configparser.ConfigParser()

        config['API'] = {}
        if self.current_api_key is not None:
            config['API']['current_api_key'] = self.current_api_key

        config['GROUP'] = {}
        if self.target_group is not None:
            config['GROUP']['target_group'] = self.target_group

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
        if not any(group['id'] == group_id for group in self.groups):
            self.groups.append({'name': group_name, 'id': group_id})
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

        self.target_group = target_group
        self.save()

    def get_target_group_name(self):
        if self.target_group is None:
            return None

        for group in self.groups:
            if group['id'] == self.target_group:
                return group['name']
        
        return None

    def is_authenticated(self):
        return self.current_api_key is not None
    