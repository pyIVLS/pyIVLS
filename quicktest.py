import sys 
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt

class testWidger(QtWidgets.QDialog):
    def __init__(self, items=['item1', 'item2', 'item3']):
        super().__init__()
        uic.loadUi('components/pyIVLS_pluginloader.ui', self)
        self.listWidget = self.findChild(QtWidgets.QListWidget, 'pluginList')
        self.populate_list(items)

    def populate_list(self, items):
        self.listWidget.clear()
        for item in items:
            list_item = QtWidgets.QListWidgetItem(item)
            list_item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget.addItem(list_item)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = testWidger()
    widget.show()
    sys.exit(app.exec())