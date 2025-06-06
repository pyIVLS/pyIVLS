## How to add plugins OUT OF DATE 26.5.2025.
1. Add plugin info to the pyIVLS.ini 
2. Create a folder for the plugin with the name {plugin name}
3. Place the source files in the folder, name it {plugin name}.py
4. Add an .ui file with the name {plugin name}_settings widget.ui under the same directory
5. Add hook implementation file in /plugins with the name pyIVLS_{plugin name}.py
6. In the hook implementation file, make a class pyIVLS_{plugin name}_plugin that inherits from the base class plugin. (defined in plugin.py)

See current plugins for a template. Consistent naming is the key to get the plugins to show up and register properly.
If you want methods to be private and not passed on hookcalls, add "_" to the beginning of the method name.


# What methods should a plugin have, the necessary interface:
- parse_settings_widget. SeqBuilder assumes this and uses it to check settings for plugins.
- 

# On writing hooks
-All args have to be named when the hook is called
for instance:
pm.hook.mm_move(1,0,0,0) crashes
pm.hook.mm_move(speed=1, x=0, y=0, z=0) works


# ini file:
Write dependencies with no spaces and comma separated values.


