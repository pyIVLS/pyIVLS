from PyQt6.QtCore import QObject, pyqtSignal
 
class AffineMDIGUI(QObject):
    """UNUSED

    Args:
        QObject (_type_): _description_
    """
    def __init__(self, MDIwidget):
        super().__init__()
        self.MDIwidget = MDIwidget
        self.setup_ui()

        # internal state initialization



    def setup_ui(self):
        # Initialize the GUI components here
        pass

    def show(self):
        # Logic to display the GUI
        pass

    def close(self):
        # Logic to close the GUI
        pass

    def update(self):
        # Logic to update the GUI components
        pass