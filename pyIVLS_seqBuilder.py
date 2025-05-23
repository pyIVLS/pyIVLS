# File: pyIVLS_seqBuilder.py
# GUI and functionality for the sequence builder in the QtDockWindow
#
# ver. 0.1
# ivarad
#25.05.21
from os.path import sep
import os
import copy

from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QFileDialog

from pathvalidate import is_valid_filename
import json

class pyIVLS_seqBuilder(QObject):

    #### Signals for communication

    info_message = pyqtSignal(str) 

    #### Slots for communication
    @pyqtSlot(dict, list)
    def getPluginFunctions(self, plugin_dict, plugin_functions):
        """Populates the list of available functions for building sequencies. This is called from the container signal "seqComponents_signal".

        Args:
            plugin_dict: dict of available plugins needed to extract class (step or loop)
            plugin_functions: list of available functions returned by plugins
        """
        self.widget.comboBox_function.currentIndexChanged.disconnect(self.update_classView)
        self.available_instructions = {}
        self.widget.comboBox_function.clear()
        for plugin in plugin_dict:
            if not plugin_dict[plugin]["load"] == 'True':
                continue
            if ("step" in plugin_dict[plugin]["class"]) or ("loop" in plugin_dict[plugin]["class"]):
                self.widget.comboBox_function.addItem(plugin)
                class_list = []
                if "step" in plugin_dict[plugin]["class"]:
                    class_list.append("step")
                if "loop" in plugin_dict[plugin]["class"]:
                    class_list.append("loop")
                for functions in plugin_functions:
                    if plugin in functions:
                       self.available_instructions[plugin] = {"class":class_list, "functions":functions[plugin]}
                       break
        self.widget.comboBox_function.addItem("loop end")
        self.widget.comboBox_function.currentIndexChanged.connect(self.update_classView)
        self.update_classView()
    #### external functions
    
    
    #### Internal functions
    def __init__(self, path):
        super(pyIVLS_seqBuilder,self).__init__()
        ui_file_name = path + "components" + sep + "pyIVLS_seqBuilder.ui"
        self.widget = uic.loadUi(ui_file_name)
        self.path = path
        
        self._connect_signals()
        self._init_treeView()
        

    def _init_treeView(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Step function", "Step class"])
        self.item = QStandardItem("pyIVLS measurement sequence")
        self.model.appendRow(self.item)
        self.update_treeView()

        
    def _connect_signals(self):
        self.widget.comboBox_function.currentIndexChanged.connect(self.update_classView)
        self.widget.addInstructionButton.clicked.connect(self._addInstructionAction)
        self.widget.saveButton.clicked.connect(self._saveRecipeAction)
        self.widget.readButton.clicked.connect(self._readRecipeAction)
        self.widget.directoryButton.clicked.connect(self._getAddress)
        self.widget.runButton.clicked.connect(self._runAction)
        
        
            #### GUI functions
    def update_classView(self):
        self.widget.comboBox_class.clear()
        if not (self.widget.comboBox_function.currentText() == '' or self.widget.comboBox_function.currentText() == 'loop end'):
          for item in self.available_instructions[self.widget.comboBox_function.currentText()]["class"]:
              self.widget.comboBox_class.addItem(item)
                
    def update_treeView(self):
        self.widget.treeView.setModel(self.model)
        self.widget.treeView.expandAll()
        
    def _getAddress(self):
        address = self.widget.lineEdit_path.text()
        if not(os.path.exists(address)):
                address = self.path
        address = QFileDialog.getExistingDirectory(None, "Select directory for saving", address, options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if address:
                self.widget.lineEdit_path.setText(address)

    def _saveRecipeAction(self):
        filename = self.widget.lineEdit_filename.text()
        if not is_valid_filename(filename):
                self.info_message.emit("Can not save sequence. Filename is invalid.")
                return 1
        with open(self.widget.lineEdit_path.text() + sep + filename, 'w') as file:
                json.dump(self.extract_data(self.model.invisibleRootItem().child(0)), file, indent=4)
        
    def _readRecipeAction(self):
        filename = QFileDialog.getOpenFileName(None, "Open pyIVLS sequence file", self.path,"json (*.json);; all (*.*)")
        with open(filename[0], 'r') as file:
            data = json.load(file)
        self._init_treeView()
        stack = copy.deepcopy(data) #### it is necessary to make sure that we did not modify original data
        looping = [] #this will keep track of the steps inside the loop, every element is +1 depth to hierarchy level, value of the element is amount of steps left on the hierechy level
        while not stack == []:
            stackItem = stack.pop(0)
            if not looping == []:
                if looping[-1] == 0:
                    self.item = self.item.parent()
                    looping.pop(-1)
                else:
                    looping[-1] = looping[-1] -1
            nextItem = QStandardItem(stackItem["function"])
            nextItem.setData(stackItem["settings"], Qt.ItemDataRole.UserRole)
            self.item.appendRow([nextItem, QStandardItem(stackItem["class"])])
            if stackItem["class"] == 'loop':
                    looping.append(len(stackItem["looping"]))
                    stack = stackItem["looping"] + stack
                    self.item = nextItem

        
            #### Sequence functions
    def _addInstructionAction(self):
        instructionFunc = self.widget.comboBox_function.currentText()
        if instructionFunc == '':
            self.info_message.emit("Instruction function can not be empty")
            return 1
        if instructionFunc == 'loop end':
            if self.item.parent() == None:
                self.info_message.emit("Can not end loop as there are no not finished loops")
                return 1
            else:
                self.item = self.item.parent() 
                return 0
        status, instructionSettings = self.available_instructions[instructionFunc]["functions"]["parse_settings_widget"]()
        if status:
            self.info_message.emit(instructionSettings["Error message"])
            return 1
        instructionClass = self.widget.comboBox_class.currentText()
        nextItem = QStandardItem(instructionFunc)
        nextItem.setData(instructionSettings, Qt.ItemDataRole.UserRole)
        self.item.appendRow([nextItem, QStandardItem(instructionClass)])
        if instructionClass == "loop":
            self.item = nextItem
        self.update_treeView()

    def extract_data(self, item):
        """Recursively extract the visible and hidden data from the model"""
        data = []
        # Recursively extract data from children
        for row in range(item.rowCount()):
            step_data = {}
            step_data['function'] = item.child(row,0).text()
            step_data['class'] = item.child(row,1).text()
            step_data['settings'] = item.child(row,0).data(Qt.ItemDataRole.UserRole)
            if item.child(row,0).rowCount()>0:
                step_data['looping'] = self.extract_data(item.child(row,0))
            data.append(step_data)
        return data
    
    def _runAction(self):
        ###############Main logic of iteration: 0 - no iterations, 1 - only start point, 2 - start end end point, iterstep = (end-start)/(iternum -1). Check with back voltage on sweep
        data = self.extract_data(self.model.invisibleRootItem().child(0))
        stack = copy.deepcopy(data) #### it is necessary to make sure that we did not modify original data
        looping = [] #this will keep track of the steps inside the loop, every element is a dict[{looping -the steps to repeat, loopFunction - looping Function, totalSteps - number of steps in loop, currentStep, totalIterations, currentIteration}]

        while ((not stack == []) or (not looping == [])):

            if not looping == []:
                if looping[-1]["currentStep"] == 0:
                    ####set next looping iteration with loopingFunction
                    looping[-1]["currentIteration"] = looping[-1]["currentIteration"] + 1
                    looping[-1]["currentStep"] = looping[-1]["currentStep"] + 1
                elif looping[-1]["currentStep"] == looping[-1]["totalSteps"]:
                    if looping[-1]["currentIteration"] < looping[-1]["totalIterations"]:
                        looping[-1]["currentStep"] = 0
                        stack = looping[-1]["looping"] + stack
                    else:
                        looping.pop(-1)
                    continue
                else:
                    looping[-1]["currentStep"] = looping[-1]["currentStep"] + 1
            stackItem = stack.pop(0)
            nextStepFunction = stackItem["function"]
            nextStepSettings = stackItem["settings"]
            nextStepClass = stackItem["class"]
            if nextStepClass == 'step':
                    print(nextStepFunction)
                    #set settings to plugin
                    #execute step
            if nextStepClass == 'loop':
                    ### set settings to plugin
                    ### get totalItrations
                    iter = 2
                    print(f"loop add steps {len(stackItem['looping'])}")
                    looping.append({"looping":stackItem["looping"], "loopFunction": nextStepFunction,"totalSteps":len(stackItem["looping"]), "currentStep":0,"totalIterations":iter, "currentIteration":0})
                    stack = stackItem["looping"] + stack
