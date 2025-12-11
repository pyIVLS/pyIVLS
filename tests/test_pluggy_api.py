import sys
import os
import pytest
import importlib
import logging
from pluggy import PluginManager
import configparser

from plugins.pyIVLS_hookspec import pyIVLS_hookspec

# Ensure a Qt application exists for plugins that create Qt objects
try:
    from PyQt6.QtWidgets import QApplication

    HAVE_QT = True
    QT_IMPORT_ERROR = None
except Exception as e:
    HAVE_QT = False
    QT_IMPORT_ERROR = e

# Add the plugins directory to the path so we can import the module
PLUGINS_DIR = "plugins"
LOGGER = logging.getLogger(__name__)
PATH = os.path.dirname(os.path.abspath(__file__))

# path stuff, add plugins dir, components dir to path
sys.path.append(os.path.join(PATH, "..", "components"))
sys.path.append(os.path.join(PATH, "..", PLUGINS_DIR))


@pytest.fixture(scope="session", autouse=True)
def ensure_qt_app():
    """Create a headless Qt application for tests that instantiate plugins.

    Uses offscreen platform to avoid display requirements in CI/headless.
    """
    if not HAVE_QT:
        pytest.skip(f"PyQt6 not available: {QT_IMPORT_ERROR}")
    # Prefer offscreen; if unavailable, QApplication will still initialize
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def find_ini_file(dir_path):
    for file in os.listdir(dir_path):
        if file.endswith(".ini"):
            return os.path.join(dir_path, file)
    return None


# Resolve plugin root path and enumerate ALL plugin directories at import time
PLUGINS_PATH = os.path.join(PATH, "..", PLUGINS_DIR)
ALL_PLUGIN_DIRS = [os.path.join(PLUGINS_PATH, d) for d in os.listdir(PLUGINS_PATH) if os.path.isdir(os.path.join(PLUGINS_PATH, d)) and not d.startswith("__")]


def build_standalone_plugin_list(plugin_dirs):
    """Build a list of plugins that have no dependencies"""
    standalone_plugins = []
    for plugin_dir in plugin_dirs:
        ini_file = find_ini_file(plugin_dir)
        assert ini_file is not None
        ini = configparser.ConfigParser()
        ini.read(ini_file)
        dependencies = ini["plugin"].get("dependencies", "").strip()
        if dependencies == "":
            standalone_plugins.append(plugin_dir)
    return standalone_plugins


STANDALONE_PLUGINS = build_standalone_plugin_list(ALL_PLUGIN_DIRS)


def import_pyIVLS_plugin(dir_path):
    # find .ini file in dir_path
    ini_file = find_ini_file(dir_path)
    assert ini_file is not None
    LOGGER.info(f"Found plugin ini file: {ini_file}")

    ini = configparser.ConfigParser()
    ini.read(ini_file)
    plg_name = ini["plugin"]["name"]
    module_name = f"pyIVLS_{plg_name}"
    sys.path.append(dir_path)

    module = importlib.import_module(module_name)
    return module


def load_plugin_instance(dir_path):
    """Load and instantiate the plugin class from a plugin directory.

    Returns: (instance, plugin_name)
    """
    ini_file = find_ini_file(dir_path)
    assert ini_file is not None
    ini = configparser.ConfigParser()
    ini.read(ini_file)
    plg_name = ini["plugin"]["name"]
    module_name = f"pyIVLS_{plg_name}"
    class_name = f"pyIVLS_{plg_name}_plugin"
    sys.path.append(dir_path)
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, class_name)
    instance = plugin_class()
    return instance, plg_name


def build_plugin_data(dir_path) -> dict:
    """Construct minimal plugin_data expected by plugins' get_setup_interface."""

    ini_file = find_ini_file(dir_path)
    assert ini_file is not None
    ini = configparser.ConfigParser()
    ini.read(ini_file)
    plg_name = ini["plugin"]["name"]
    plg_function = ini["plugin"]["function"]

    # build the settings dict from .ini
    settings = {}
    ini_sett = ini["settings"]
    for key in ini_sett:
        settings[key] = ini_sett[key]

    plugin_data = {}
    plugin_data[plg_name] = {
        "function_dict": {},
        "settings": settings,
    }
    return plugin_data, plg_name, plg_function


class TestPluginAPI:
    """Test the FileManager class for file header creation."""

    def setup_method(self):
        """Set up test fixtures."""

    @pytest.mark.parametrize(
        "plugin_dir",
        ALL_PLUGIN_DIRS,
        ids=[os.path.basename(p) for p in ALL_PLUGIN_DIRS],
    )
    def test_plugin_import(self, plugin_dir):
        """Import each plugin directory independently for clearer failures."""
        module = import_pyIVLS_plugin(plugin_dir)
        assert module is not None
        LOGGER.info(f"Imported plugin module: {module}")

    @pytest.mark.parametrize(
        "plugin_dir",
        STANDALONE_PLUGINS,
        ids=[os.path.basename(p) for p in STANDALONE_PLUGINS],
    )
    def test_standalone_plugin_hooks(self, plugin_dir):
        pm = PluginManager("pyIVLS")
        pm.add_hookspecs(pyIVLS_hookspec)
        instance, plg_name = load_plugin_instance(plugin_dir)
        name = pm.register(instance)
        assert name is not None

        # Provide minimal function_dict to plugins prior to setup
        plugin_data, plg_name, plg_function = build_plugin_data(plugin_dir)
        pm.hook.set_function(function_dict=plugin_data[plg_name]["function_dict"])

        setup_intf = pm.hook.get_setup_interface(plugin_data=plugin_data)
        assert isinstance(setup_intf, list)
        LOGGER.info(f"Testing plugin {name} setup interface with return: {setup_intf}")
        for item in setup_intf:
            assert item is None or isinstance(item, dict)
        LOGGER.info(f"Setup interface from plugin {name}: {setup_intf}")

        mdi_intf = pm.hook.get_MDI_interface()
        assert isinstance(mdi_intf, list)
        for item in mdi_intf:
            assert item is None or isinstance(item, dict)

        funcs = pm.hook.get_functions()
        assert isinstance(funcs, list)
        # first item corresponds to our plugin since it is the only one registered

        plg_return = funcs[0]
        assert isinstance(plg_return, dict)
        # funct dict is a nested dict of (plg name: (function name: function obj)) 
        func_dict = plg_return[plg_name]

        # check that all returned functions are callable and that return type is correct
        # expected:
        # return [4, {"Error message": "Sutter device change error"}]

        for func_name, func in func_dict.items():
            LOGGER.info(f"Testing plugin {name} function: {func_name}")
            assert callable(func), f"Function {func_name} is not callable"
            status, state = func()
            assert isinstance(status, int), f"Function {func_name} did not return int status"
            assert isinstance(state, dict), f"Function {func_name} did not return dict state"
            #assert "Error message" in state, f"Function {func_name} state dict missing 'Error message' key"

        missed = pm.hook.set_function(function_dict={})
        assert isinstance(missed, list)

        plg_ref = pm.hook.get_plugin()
        assert plg_ref == [], "get_plugin is being deprecated, should not have implementations"

        log = pm.hook.get_log()
        assert isinstance(log, list)
        for item in log:
            assert item is None or isinstance(item, dict)

        info = pm.hook.get_info()
        assert isinstance(info, list)
        for item in info:
            assert item is None or isinstance(item, dict)

        cl = pm.hook.get_closeLock()
        assert isinstance(cl, list)
        for item in cl:
            assert item is None or isinstance(item, dict)

        settings = pm.hook.get_plugin_settings()
        assert isinstance(settings, list)
        for item in settings:
            assert item is None or (isinstance(item, tuple) and len(item) == 3 and isinstance(item[0], str) and isinstance(item[1], int) and isinstance(item[2], dict))
