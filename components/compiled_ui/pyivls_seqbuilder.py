################################################################################
## Form generated from reading UI file 'pyIVLS_seqBuilder.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTreeView,
    QVBoxLayout,
)


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1069, 746)
        Form.setMinimumSize(QSize(750, 0))
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.recipeBox = QGroupBox(Form)
        self.recipeBox.setObjectName("recipeBox")
        self.verticalLayout_4 = QVBoxLayout(self.recipeBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_Function = QLabel(self.recipeBox)
        self.label_Function.setObjectName("label_Function")

        self.horizontalLayout_5.addWidget(self.label_Function)

        self.comboBox_function = QComboBox(self.recipeBox)
        self.comboBox_function.setObjectName("comboBox_function")

        self.horizontalLayout_5.addWidget(self.comboBox_function)

        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_class = QLabel(self.recipeBox)
        self.label_class.setObjectName("label_class")

        self.horizontalLayout_4.addWidget(self.label_class)

        self.comboBox_class = QComboBox(self.recipeBox)
        self.comboBox_class.setObjectName("comboBox_class")

        self.horizontalLayout_4.addWidget(self.comboBox_class)

        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.testButton = QPushButton(self.recipeBox)
        self.testButton.setObjectName("testButton")

        self.gridLayout.addWidget(self.testButton, 0, 1, 1, 1)

        self.addInstructionButton = QPushButton(self.recipeBox)
        self.addInstructionButton.setObjectName("addInstructionButton")

        self.gridLayout.addWidget(self.addInstructionButton, 0, 0, 1, 1)

        self.readSettingsButton = QPushButton(self.recipeBox)
        self.readSettingsButton.setObjectName("readSettingsButton")

        self.gridLayout.addWidget(self.readSettingsButton, 1, 0, 1, 1)

        self.updateSettings = QPushButton(self.recipeBox)
        self.updateSettings.setObjectName("updateSettings")

        self.gridLayout.addWidget(self.updateSettings, 1, 1, 1, 1)

        self.verticalLayout_4.addLayout(self.gridLayout)

        self.verticalLayout_2.addWidget(self.recipeBox)

        self.fileBox = QGroupBox(Form)
        self.fileBox.setObjectName("fileBox")
        self.fileBox.setEnabled(True)
        self.verticalLayout_3 = QVBoxLayout(self.fileBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pathLabel = QLabel(self.fileBox)
        self.pathLabel.setObjectName("pathLabel")
        self.pathLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_6.addWidget(self.pathLabel)

        self.lineEdit_path = QLineEdit(self.fileBox)
        self.lineEdit_path.setObjectName("lineEdit_path")

        self.horizontalLayout_6.addWidget(self.lineEdit_path)

        self.directoryButton = QPushButton(self.fileBox)
        self.directoryButton.setObjectName("directoryButton")

        self.horizontalLayout_6.addWidget(self.directoryButton)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.filenameLabel = QLabel(self.fileBox)
        self.filenameLabel.setObjectName("filenameLabel")
        self.filenameLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_7.addWidget(self.filenameLabel)

        self.lineEdit_filename = QLineEdit(self.fileBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.horizontalLayout_7.addWidget(self.lineEdit_filename)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_9)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_10)

        self.saveButton = QPushButton(self.fileBox)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setEnabled(True)

        self.horizontalLayout_10.addWidget(self.saveButton)

        self.readButton = QPushButton(self.fileBox)
        self.readButton.setObjectName("readButton")
        self.readButton.setEnabled(True)

        self.horizontalLayout_10.addWidget(self.readButton)

        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.verticalLayout_2.addWidget(self.fileBox)

        self.execBox = QGroupBox(Form)
        self.execBox.setObjectName("execBox")
        self.verticalLayout_5 = QVBoxLayout(self.execBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.runButton = QPushButton(self.execBox)
        self.runButton.setObjectName("runButton")

        self.horizontalLayout_2.addWidget(self.runButton)

        self.stopButton = QPushButton(self.execBox)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.stopButton)

        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.addWidget(self.execBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.treeView = QTreeView(Form)
        self.treeView.setObjectName("treeView")
        self.treeView.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.treeView.setDefaultDropAction(Qt.DropAction.IgnoreAction)

        self.horizontalLayout.addWidget(self.treeView)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.recipeBox.setTitle("")
        self.label_Function.setText(QCoreApplication.translate("Form", "Sequence instruction function", None))
        self.label_class.setText(QCoreApplication.translate("Form", "Sequence instruction class", None))
        self.testButton.setText(QCoreApplication.translate("Form", "Test", None))
        self.addInstructionButton.setText(QCoreApplication.translate("Form", "Add instruction", None))
        self.readSettingsButton.setText(QCoreApplication.translate("Form", "Read settings to GUI", None))
        self.updateSettings.setText(QCoreApplication.translate("Form", "Update settings for all plugins", None))
        self.fileBox.setTitle("")
        self.pathLabel.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.filenameLabel.setText(QCoreApplication.translate("Form", "Filename", None))
        self.saveButton.setText(QCoreApplication.translate("Form", "save", None))
        self.readButton.setText(QCoreApplication.translate("Form", "read", None))
        self.execBox.setTitle("")
        self.runButton.setText(QCoreApplication.translate("Form", "run", None))
        self.stopButton.setText(QCoreApplication.translate("Form", "stop", None))

    # retranslateUi
