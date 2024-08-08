## How to add plugins:

1. Add plugin info to the pyIVLS.ini 
2. Check pyIVLS_hookspec.py for hooks that *must* be implemented if the plugin is of a spesific type
3. Add a folder for the python files, the name of the folder does not matter.
4. Place the source files in the folder, name it {plugin name}.py
5. Add an .ui file with the name {plugin name}_settings widget.ui
6. Add hook implementation file in /plugins with the name pyIVLS_{plugin name}.py


# On writing hooks
-All args have to be named when the hook is called