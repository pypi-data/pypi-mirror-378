"""
HATS Plugin Loader
Auto-discovers and loads plugins from the plugins/ directory.
"""
import os
import importlib.util

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")

def load_plugins(engine):
    if not os.path.isdir(PLUGIN_DIR):
        return
    for fname in os.listdir(PLUGIN_DIR):
        if fname.endswith(".py") and not fname.startswith("_"):
            path = os.path.join(PLUGIN_DIR, fname)
            spec = importlib.util.spec_from_file_location(fname[:-3], path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    mod.register(engine)
