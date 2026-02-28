import json
import os

class I18n:
    """Поддержка локализации системных ответов Xilla"""
    def __init__(self, config_manager):
        self.lang = config_manager.get("core", "language", "ru")
        self.strings = {}
        self.load_lang(self.lang)

    def load_lang(self, lang):
        path = os.path.join(os.getcwd(), "locales", f"{lang}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
        else:
            self.strings = {}

    def t(self, key, default=None):
        return self.strings.get(key, default or key)
