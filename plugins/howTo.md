# Adding plugins:
TODO: update instructions
## How to add plugins:
1. Copy the template
2. Implement necessary hooks, update imports etc. 
3. Fill in the provided .ini template
4. In the GUI, open the pluginloader subwindow
4. import plugin, the loader handles basic checks and updates the global config.
The name given in the ini file should match the file pyIVLS_{name}.py and the object inside pyIVLS_{name}_plugin. Otherwise naming is not important.
The address (dir) of the plugin is read on import, so the dir can have any name. The .ini file is also loaded while importing, so the name of the .ini file does not matter.

## How to remove plugins:
Currently removing plugins is only available by removing them from pyIVLS.ini

## What methods should a plugin have, the necessary interface:
TODO: complete this section.
- parse_settings_widget. SeqBuilder assumes this and uses it to check settings for plugins. 
- Seqbuilder also assumes "setSettings" to set current state for plugins
- "getIterations" 
 
## hookcall footguns
All args have to be named when the hook is called,
for instance:

- pm.hook.mm_move(1,0,0,0) crashes
- pm.hook.mm_move(speed=1, x=0, y=0, z=0) works


## ini file:
Write dependencies with no spaces and comma separated values.


# Core ideas for plugin structure:
## plugin_components.py
Provides a library of common funcionality for plugins. 

## Low level
plugin functionality implemented in a low level class that works by itself. The low level should not use the components in this file. Low level class should raise exceptions on errors? The errors are caught by the plugin GUI class.

## GUI
plugin GUI functionality implemented in a separate class that uses the low level class. The plugin GUI class can use the components provided by plugin_components. GUIs should not raise exceptions(?), but return PyIVLSReturn objects. This allows for handling inter-plugin errors in a standardized way.
plugin GUIs shouldn't inherit from any base class nor from QObject. I would prefer to keep it that way and offload all qt-related functionality to components. 
This also helps in keeping the GUI implementation relatively clean.
Most of the common functionality should be moved to a component, since:
1. Reduce repetitive code, make it easier to maintain with a single point of change (not rewriting all plugins on all changes)
2. Make it easier to implement new plugins, since the common functionality is already implemented
3. Way way way easier to test the components than all plugins by themselves.

## hookspecs
TODO

## FOOTGUNS:
Dont use uppercase in naming, since:
When creating a field in the .ini file to save last saved plugins, the names are compressed to all lowercase.
Don't use spaces. in the "function" field. This is because the dependencies are saved under the type field name, and the ini file does not allow spaced in the names with the current configuration.
 