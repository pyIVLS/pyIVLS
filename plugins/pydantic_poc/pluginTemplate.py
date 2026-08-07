"""
This is a template for a plugin core implementation in pyIVLS
This file should be independent on GUI, i.e. it should be made in a way that allows to reuse it in other scripts
"""


class pluginTemplate:
    def __init__(self):
        self.int_var = True

    def core_functionality(self, arg1: float, arg2: float) -> bool:
        """This is an example of a core functionality function. It should be implemented in a way that it can be used outside of GUI.
        Args:
            arg1 (float):
            arg2 (float):
        Returns:
            bool: Success or failure of the function
        """
        if arg1 > arg2:
            return True
        else:
            return False

    def get_internal_state(self) -> dict:
        """This is an example of a function that returns the internal state of the plugin. 
            dict: A dictionary containing the internal state of the plugin
        """
        return {"int_var": self.int_var}

    def will_fail(self) -> bool:
        """This will fail
        Returns:
            bool: This function always returns False to indicate failure
        """
        return False
