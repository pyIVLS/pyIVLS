################################################################################
## Form generated from reading UI file 'pyIVLS_GUI.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMdiArea, QMenu, QMenuBar, QStatusBar, QVBoxLayout, QWidget


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1034, 899)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionPlugins = QAction(MainWindow)
        self.actionPlugins.setObjectName("actionPlugins")
        self.actionSequence_builder = QAction(MainWindow)
        self.actionSequence_builder.setObjectName("actionSequence_builder")
        self.actionSequence_builder.setCheckable(True)
        self.actionSequence_builder.setChecked(True)
        self.actionDockWidget = QAction(MainWindow)
        self.actionDockWidget.setObjectName("actionDockWidget")
        self.actionDockWidget.setCheckable(True)
        self.actionDockWidget.setChecked(True)
        self.actionMDI_windows = QAction(MainWindow)
        self.actionMDI_windows.setObjectName("actionMDI_windows")
        self.actionMDI_windows.setCheckable(False)
        self.actionMDI_windows.setChecked(False)
        self.actionSequence_builder1 = QAction(MainWindow)
        self.actionSequence_builder1.setObjectName("actionSequence_builder1")
        self.actionSequence_builder1.setCheckable(True)
        self.actionSequence_builder1.setChecked(True)
        self.actionDockWidget1 = QAction(MainWindow)
        self.actionDockWidget1.setObjectName("actionDockWidget1")
        self.actionDockWidget1.setCheckable(True)
        self.actionDockWidget1.setChecked(True)
        self.MdiMenu = QAction(MainWindow)
        self.MdiMenu.setObjectName("MdiMenu")
        self.actionWrite_settings_to_file = QAction(MainWindow)
        self.actionWrite_settings_to_file.setObjectName("actionWrite_settings_to_file")
        self.actionRead_config_file = QAction(MainWindow)
        self.actionRead_config_file.setObjectName("actionRead_config_file")
        self.actionExport_config_file = QAction(MainWindow)
        self.actionExport_config_file.setObjectName("actionExport_config_file")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName("mdiArea")

        self.verticalLayout_2.addWidget(self.mdiArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1034, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuShow = QMenu(self.menuView)
        self.menuShow.setObjectName("menuShow")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionWrite_settings_to_file)
        self.menuFile.addAction(self.actionRead_config_file)
        self.menuFile.addAction(self.actionExport_config_file)
        self.menuView.addAction(self.menuShow.menuAction())
        self.menuShow.addAction(self.actionSequence_builder)
        self.menuShow.addAction(self.actionDockWidget1)
        self.menuTools.addAction(self.actionPlugins)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About", None))
        self.actionPlugins.setText(QCoreApplication.translate("MainWindow", "Plugins", None))
        self.actionSequence_builder.setText(QCoreApplication.translate("MainWindow", "Sequence builder", None))
        self.actionDockWidget.setText(QCoreApplication.translate("MainWindow", "Settings", None))
        self.actionMDI_windows.setText(QCoreApplication.translate("MainWindow", "MDI windows", None))
        self.actionSequence_builder1.setText(QCoreApplication.translate("MainWindow", "Sequence builder", None))
        self.actionDockWidget1.setText(QCoreApplication.translate("MainWindow", "Settings", None))
        self.MdiMenu.setText(QCoreApplication.translate("MainWindow", "MDI windows", None))
        self.actionWrite_settings_to_file.setText(QCoreApplication.translate("MainWindow", "Write plugin settings to file", None))
        self.actionRead_config_file.setText(QCoreApplication.translate("MainWindow", "Import config file", None))
        self.actionExport_config_file.setText(QCoreApplication.translate("MainWindow", "Export config file", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "View", None))
        self.menuShow.setTitle(QCoreApplication.translate("MainWindow", "Show", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", "Tools", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help", None))

    # retranslateUi
