# Plugin API and provided components

## Hooks, the main interface for plugin-plugin communication:
All of the possible hooks are written in the [hookspec file](../plugins/pyIVLS_hookspec.py). Implementations for these may be written if the plugin needs that functionality. The [plugin_components](../plugins/plugin_components.py) file provides common helpers to implement some of the hooks.  The current hooks are:

```python 
def get_setup_interface(self, plugin_data: dict) -> dict:
```
This returns the settings widget for the plugin to be placed in the tabWidget of the main window. The given argument includes the initial settings parsed from the .ini file by the plugincontainer. Return type as a single element dictionary of the name of the plugin as key and the settingsWidget as a value.

```python 
def get_MDI_interface(self, args=None) -> dict:
```
This returns an MDI widget to be inserted into the MDIWindow of the mainwindow. Return type as a single element dictionary of the name of the plugin as key and the MDIWidget as a value.

```python 
def get_function(self, args=None):
```
This hook returns a list of publicly available functions to be used by other plugins and the sequenceBuilder. This is the core functionality that enables plugin-plugin communication. Returns a nested dictionary in the format dict["name_of_plugin" : dict["name_of_method" : callable()]]. The [plugin_components](../plugins/plugin_components.py) file provides a function get_public_methods() that parses all available methods decorated with the @public decorated provided in the same file.

```python 
def set_function(self, function_dict):
```
This hook needs to be defined for plugins that depend on other plugins. It gets a function dictionary as an argument in the format dict["plugin_function" : dict["name_of_plugin" : dict["name_of_method" : callable()]]], so a nested dictionary with a a top dictionary of different plugin functions, all of which contain the dictionaries for plugins of that function.
 

```python 
def get_plugin(self, args=None):
```
This hook is not implemented for any plugin and no part of the program uses this hook. The point was to get the plugin as an object, but just passing the functions seems to be a safer way to do this. It should then save this internally for further use.

```python 
def set_plugin(self, plugin_list, args=None):
```
This hook is not implemented for any plugin and no part of the program uses this hook. 


```python 
def get_log(self, args=None):
```
If using logging_helper, this is provided by logger.log_signal. 
Return type as a single element dictionary of the name of the plugin as key and the logging signal as a value.

```python 
def get_info(self, args=None):
```
If using logging_helper, this is provided by logger.info_popup_signal. 
Return type as a single element dictionary of the name of the plugin as key and the info popup signal as a value.

```python 
def get_closeLock(self, args=None):
```
If using CloseLockSignalProvider, this is provided by CloseLockSignalProvider.closeLock.
Return type as a single element dictionary of the name of the plugin as key and the closelock signal as a value.

```python 
def get_plugin_settings(self, args=None):
```
The current standard is calling parse_settings_widget for the plugin and returning that result. The parsing is done in the plugin container which calls this. The key names in the dictionary should match the .ini file of the plugin.
Return type as a tuple of ("plugin_name", parse status in the standard pyIVLS format, settings dictionary) 


## Public Methods that are assumed for different types of plugins:
Plugins that have settings widgets, or are used as depenencies for other plugins:
- parse_settings_widget with a return of a tuple (pyIVLS_status_code: int, settings dictionary). Best practice is to return the dictionary with the same key names as the .ini file has in order for everything to work together.
- setSettings() -> none to set the internal settings dictionary

Plugins that are integrated to use seqBuilder
- set_gui_from_settings() -> None, to set the GUI from the settings stored in the seqbuilder
- sequenceStep(postfix: str) -> (status, state), provides the functionality for a single step in the sequence.
- getIterations() -> int, returns the number of iterations for a looping plugin. Return used internally in seqBuilder.
- loopingIteration(currentIteration: int) -> (status, iterText), Provides the functionality for a single iteration of a loop. For example, moving the probes to a single measurement point in the affineMove plugin. 

## SettingsWidgets:
- USE ALL FUNCTIONALITY THAT QT HAS TO OFFER: If you need an inputwidget that only accepts integers in a certain range, use a spinbox and not a lineInput. This reduces boilerplate and makes it easier for everything to just work. Examples:
    - address, path, etc -> Line edit, text edit. Parsed in the code
    - integer -> spin box
    - float -> double spin box
    - numerical in a certain range -> slider or spinbox with limits
    - choose from predefined set (for example, which dependency to use) -> combobox
- All settings input fields should preferably be populated in the code instead of through the saved settingsWidget. This again reduces the chances of user error by removing default values
- All settingswidgets should be wrapped in scrollbars so that the whole settings tab can be scaled to be smaller when working on a small screen.
- If the settings widget is in a relatively stable state with few modifications coming, I think it should be compiled into python code instead of reading the UI-file. This provides static analysis and code completion when using a compatible IDE.



## Best practices:
- Keep an internal settings dictionary for the plugin. This is to make sure that unwanted GUI changes are not transferred to the run settings
