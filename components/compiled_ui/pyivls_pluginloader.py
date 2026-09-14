################################################################################
## Form generated from reading UI file 'pyIVLS_pluginloader.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtWidgets import QGroupBox, QPushButton, QSizePolicy, QTableWidget, QVBoxLayout


class Ui_pyIVLSpluginloader:
    def setupUi(self, pyIVLSpluginloader):
        if not pyIVLSpluginloader.objectName():
            pyIVLSpluginloader.setObjectName("pyIVLSpluginloader")
        pyIVLSpluginloader.setWindowModality(Qt.WindowModality.WindowModal)
        pyIVLSpluginloader.setEnabled(True)
        pyIVLSpluginloader.resize(600, 377)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pyIVLSpluginloader.sizePolicy().hasHeightForWidth())
        pyIVLSpluginloader.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(pyIVLSpluginloader)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QGroupBox(pyIVLSpluginloader)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pluginList = QTableWidget(self.groupBox)
        self.pluginList.setObjectName("pluginList")
        self.pluginList.setSortingEnabled(True)

        self.verticalLayout_2.addWidget(self.pluginList)

        self.verticalLayout.addWidget(self.groupBox)

        self.applyButton = QPushButton(pyIVLSpluginloader)
        self.applyButton.setObjectName("applyButton")
        self.applyButton.setEnabled(True)

        self.verticalLayout.addWidget(self.applyButton)

        self.uploadButton = QPushButton(pyIVLSpluginloader)
        self.uploadButton.setObjectName("uploadButton")

        self.verticalLayout.addWidget(self.uploadButton)

        self.retranslateUi(pyIVLSpluginloader)

        QMetaObject.connectSlotsByName(pyIVLSpluginloader)

    # setupUi

    def retranslateUi(self, pyIVLSpluginloader):
        pyIVLSpluginloader.setWindowTitle(QCoreApplication.translate("pyIVLSpluginloader", "pyIVLS plugin loader", None))
        self.groupBox.setTitle(QCoreApplication.translate("pyIVLSpluginloader", "Plugins", None))
        self.applyButton.setText(QCoreApplication.translate("pyIVLSpluginloader", "Apply", None))
        self.uploadButton.setText(QCoreApplication.translate("pyIVLSpluginloader", "Upload new plugin", None))

    # retranslateUi
