### Base class Plugin constants
HOOKS = [
    "get_setup_interface",
    "get_MDI_interface",
    "get_functions",
    "get_log",
    "get_info",
    "get_closeLock",
]


class Plugin_hookspec:
    non_public_methods = ["setup", "get_public_methods", "hookimpl"]
    non_public_methods.extend(HOOKS)

    def __init__(self, name: str, dependencies: list, function: str):
        self.name = name
        self.dependencies = dependencies
        self.function = function

    def _get_public_methods(self):
        """
        Returns a nested dictionary of public methods for the plugin
        """
        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method not in self.non_public_methods
        }
        return methods
