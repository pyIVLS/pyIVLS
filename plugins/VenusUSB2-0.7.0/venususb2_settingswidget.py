################################################################################
## Form generated from reading UI file 'VenusUSB2_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(868, 650)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 848, 630))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.exposureBox = QGroupBox(self.groupBox_general)
        self.exposureBox.setObjectName("exposureBox")
        self.horizontalLayout_2 = QHBoxLayout(self.exposureBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.exposureText = QLabel(self.exposureBox)
        self.exposureText.setObjectName("exposureText")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.exposureText.sizePolicy().hasHeightForWidth())
        self.exposureText.setSizePolicy(sizePolicy1)
        self.exposureText.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_2.addWidget(self.exposureText)

        self.exposure = QComboBox(self.exposureBox)
        self.exposure.setObjectName("exposure")

        self.horizontalLayout_2.addWidget(self.exposure)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout.addWidget(self.exposureBox)

        self.sourceBox = QGroupBox(self.groupBox_general)
        self.sourceBox.setObjectName("sourceBox")
        self.horizontalLayout = QHBoxLayout(self.sourceBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sourceText = QLabel(self.sourceBox)
        self.sourceText.setObjectName("sourceText")
        sizePolicy1.setHeightForWidth(self.sourceText.sizePolicy().hasHeightForWidth())
        self.sourceText.setSizePolicy(sizePolicy1)
        self.sourceText.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.sourceText)

        self.cameraSource = QLineEdit(self.sourceBox)
        self.cameraSource.setObjectName("cameraSource")

        self.horizontalLayout.addWidget(self.cameraSource)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.statusLabel = QLabel(self.sourceBox)
        self.statusLabel.setObjectName("statusLabel")

        self.horizontalLayout.addWidget(self.statusLabel)

        self.sourceLabel = QLabel(self.sourceBox)
        self.sourceLabel.setObjectName("sourceLabel")

        self.horizontalLayout.addWidget(self.sourceLabel)

        self.connectionIndicator = QLabel(self.sourceBox)
        self.connectionIndicator.setObjectName("connectionIndicator")
        self.connectionIndicator.setMaximumSize(QSize(20, 20))
        self.connectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout.addWidget(self.connectionIndicator)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addWidget(self.sourceBox)

        self.groupBox = QGroupBox(self.groupBox_general)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cameraPreview = QPushButton(self.groupBox)
        self.cameraPreview.setObjectName("cameraPreview")

        self.horizontalLayout_3.addWidget(self.cameraPreview)

        self.horizontalSpacer_3 = QSpacerItem(713, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout.addWidget(self.groupBox)

        self.fileBox = QGroupBox(self.groupBox_general)
        self.fileBox.setObjectName("fileBox")
        self.fileBox.setEnabled(True)
        self.verticalLayout_4 = QVBoxLayout(self.fileBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pathLabel = QLabel(self.fileBox)
        self.pathLabel.setObjectName("pathLabel")
        self.pathLabel.setMinimumSize(QSize(160, 0))

        self.horizontalLayout_5.addWidget(self.pathLabel)

        self.lineEdit_path = QLineEdit(self.fileBox)
        self.lineEdit_path.setObjectName("lineEdit_path")

        self.horizontalLayout_5.addWidget(self.lineEdit_path)

        self.directoryButton = QPushButton(self.fileBox)
        self.directoryButton.setObjectName("directoryButton")

        self.horizontalLayout_5.addWidget(self.directoryButton)

        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.filenameLabel = QLabel(self.fileBox)
        self.filenameLabel.setObjectName("filenameLabel")
        self.filenameLabel.setMinimumSize(QSize(160, 0))

        self.horizontalLayout_6.addWidget(self.filenameLabel)

        self.lineEdit_filename = QLineEdit(self.fileBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.horizontalLayout_6.addWidget(self.lineEdit_filename)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_9)

        self.verticalLayout_4.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_10)

        self.saveButton = QPushButton(self.fileBox)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setEnabled(False)

        self.horizontalLayout_9.addWidget(self.saveButton)

        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.verticalLayout.addWidget(self.fileBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_3.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Venus USB2.0 camera settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Camera settings", None))
        self.exposureBox.setTitle("")
        self.exposureText.setText(QCoreApplication.translate("Form", "Exposure time", None))
        self.sourceBox.setTitle("")
        self.sourceText.setText(QCoreApplication.translate("Form", "Source", None))
        self.cameraSource.setText("")
        self.statusLabel.setText(QCoreApplication.translate("Form", "Connection status", None))
        self.sourceLabel.setText("")
        self.connectionIndicator.setText("")
        self.groupBox.setTitle("")
        self.cameraPreview.setText(QCoreApplication.translate("Form", "preview", None))
        self.fileBox.setTitle("")
        self.pathLabel.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.filenameLabel.setText(QCoreApplication.translate("Form", "Filename", None))
        self.saveButton.setText(QCoreApplication.translate("Form", "save", None))

    # retranslateUi
