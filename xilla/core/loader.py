import os
import sys
import importlib.util
import logging
import inspect
from herokutl import events

# Magic global dict for legacy compatibility routing
sys.modules['hikka'] = sys.modules['xilla']
sys.modules['heroku'] = sys.modules['xilla']
sys.modules['geektg'] = sys.modules['xilla']
sys.modules['userbot'] = sys.modules['xilla']

class ModuleLoader:
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger("ModuleLoader")
        self.modules = []
        
    async def load_all(self):
        # 1. Load System Modules
        mod_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules")
        await self._load_dir(mod_dir)
        
        # 2. Load Plugins
        plug_dir = os.path.join(os.getcwd(), "plugins")
        await self._load_dir(plug_dir)
        
    async def _load_dir(self, directory):
        if not os.path.exists(directory):
            return
            
        for file in os.listdir(directory):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_file(os.path.join(directory, file))

    async def load_file(self, filepath):
        name = os.path.basename(filepath)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(f"xilla.dynamic.{name}", filepath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            # Find classes inheriting from Module
            for item_name, item in inspect.getmembers(mod, inspect.isclass):
                if item.__module__ == mod.__name__ and hasattr(item, "_xilla_module"):
                    instance = item()
                    instance.client = self.client
                    if hasattr(instance, "on_load"):
                        await instance.on_load()
                        
                    self._register_commands(instance)
                    self.modules.append(instance)
                    self.logger.debug(f"Loaded module {name}")
        except Exception as e:
            self.logger.error(f"Failed to load {name}: {e}")

    def _register_commands(self, instance):
        for name, method in inspect.getmembers(instance, inspect.iscoroutinefunction):
            if hasattr(method, "_xilla_command"):
                cmd_name = method._xilla_command
                
                # Herokutl Event Handler
                async def wrapper(event, method=method):
                    if event.message.out: # Default to outgoing only for now
                        # Cut prefix and command
                        text = event.raw_text
                        args = text.split(" ", 1)[1] if len(text.split()) > 1 else ""
                        event.args = args
                        try:
                            await method(event)
                        except Exception as e:
                            self.logger.error(f"Command Error: {e}")
                
                self.client.add_event_handler(wrapper, events.NewMessage(pattern=f"^\.{cmd_name}(?: |$)"))

def command(name=None):
    def decorator(func):
        func._xilla_command = name or func.__name__
        return func
    return decorator

class Module:
    _xilla_module = True
