import os
import json

CONFIG_FILE = os.path.join(os.getcwd(), "xilla.json")

def get_api_credentials():
    if "API_ID" in os.environ and "API_HASH" in os.environ:
        return int(os.environ["API_ID"]), os.environ["API_HASH"]

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data["api_id"], data["api_hash"]
        except Exception:
            pass

    print("☀️ Добро пожаловать в Xilla! Пожалуйста, введите данные от my.telegram.org:")
    api_id = input("API ID: ")
    api_hash = input("API HASH: ")
    
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_id": int(api_id), "api_hash": api_hash}, f)
        
    return int(api_id), api_hash

class ConfigManager:
    """Store modular configurations in memory and file"""
    def __init__(self):
        self.config = {}
        self._load()

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.config = data.get("modules", {})
                
    def save(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data["modules"] = self.config
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get(self, module, key, default=None):
        return self.config.get(module, {}).get(key, default)

    def set(self, module, key, value):
        if module not in self.config:
            self.config[module] = {}
        self.config[module][key] = value
        self.save()
