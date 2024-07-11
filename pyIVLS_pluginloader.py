# File: pyIVLS_pluginloader.py
# dialog and functionality for the plugins action from the Tools menu

from os.path import sep
import sys
import pyIVLS_constants


from configparser import SafeConfigParser

from PyQt6 import QtWidgets, uic 
from PyQt6.QtCore import QFile, QIODevice, pyqtSlot, QEvent

class pyIVLS_pluginloader(QtWidgets.QDialog):

  #### redefine close event####
  ##### https://stackoverflow.com/questions/52747229/pyside-uiloader-capture-close-event-signals
  ##### in fact this is very buggy and not recommended in pyQt, if smth like this is needed GUI classes should be written manually 
  def eventFilter(self, watched, event):
     if watched is self.window and event.type() == QEvent.Type.Close:
           self.redefined_closeEvent(event)
           return True
     try:
           return super(pyIVLS_pluginloader, self).eventFilter(watched, event)
     except:
           return True

  def redefined_closeEvent(self, event):
    #if self.window.disconnectButton.isEnabled() or  self.window.stopButton.isEnabled(): #or stop button is enabled
    #   self.show_message("Disconnect RTA first")
    #   event.ignore()
    #else:
    #   self.pyRTAadvancedView.window_advanced.close()
    #   event.accept()
    print('Close button clicked')
   

  def OK_button_action(self):
     print('OK button clicked')
            
  def Cancel_button_action(self):
     print('Cancel button clicked')
          
  def __init__(self, path):
      super(pyIVLS_pluginloader,self).__init__()
      print('OK') 
      ui_file_name = path + 'components' + sep + 'pyIVLS_pluginloader.ui'
      ui_file = QFile(ui_file_name)
      if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
          print("Cannot open pyIVLS_pluginloader: {ui_file.errorString()}")
          sys.exit(-1) 
      self.window = uic.loadUi(ui_file)
      ui_file.close()
      if not self.window:
         print(loader.errorString())
         sys.exit(-1)
         
      self.window.installEventFilter(self)   
      
      
      #redefining the buttons looks like a workaround. In the reality to validate the data you can use done() method of QDialog, but there is no access to it when the class is imported from *.ui
      self.window.OKButton.clicked.connect(self.OK_button_action)
      self.window.cancelButton.clicked.connect(self.Cancel_button_action)

