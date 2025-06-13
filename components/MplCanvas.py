import matplotlib

matplotlib.use("QtAgg")

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

    def _create_toolbar(self, parentWindow):
        ########### changing the color in toolbar has bug due to change in the PyQT6 opion convention  https://github.com/matplotlib/matplotlib/issues/22471/
        # File "/usr/lib/python3/dist-packages/matplotlib/backends/qt_editor/_formlayout.py", line 74, in choose_color QtWidgets.QColorDialog.ShowAlphaChannel
        # AttributeError: type object 'QColorDialog' has no attribute 'ShowAlphaChannel'

        ###it is related to modifying QtWidgets.QColorDialog.ShowAlphaChannel to QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel
        return NavigationToolbar(self, parentWindow)
