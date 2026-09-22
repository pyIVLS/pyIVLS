################################################################################
## Form generated from reading UI file 'TLCCS_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1004, 654)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QVBoxLayout(Form)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 984, 634))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.connectBox = QGroupBox(self.groupBox_general)
        self.connectBox.setObjectName("connectBox")
        self.horizontalLayout_13 = QHBoxLayout(self.connectBox)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.connectButton = QPushButton(self.connectBox)
        self.connectButton.setObjectName("connectButton")

        self.horizontalLayout_12.addWidget(self.connectButton)

        self.disconnectButton = QPushButton(self.connectBox)
        self.disconnectButton.setObjectName("disconnectButton")
        self.disconnectButton.setEnabled(False)

        self.horizontalLayout_12.addWidget(self.disconnectButton)

        self.horizontalLayout_13.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QLabel(self.connectBox)
        self.label.setObjectName("label")

        self.horizontalLayout_4.addWidget(self.label)

        self.backend_Combo = QComboBox(self.connectBox)
        self.backend_Combo.setObjectName("backend_Combo")

        self.horizontalLayout_4.addWidget(self.backend_Combo)

        self.horizontalLayout_13.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.statusLabel = QLabel(self.connectBox)
        self.statusLabel.setObjectName("statusLabel")

        self.horizontalLayout.addWidget(self.statusLabel)

        self.connectionIndicator = QLabel(self.connectBox)
        self.connectionIndicator.setObjectName("connectionIndicator")
        self.connectionIndicator.setMinimumSize(QSize(20, 20))
        self.connectionIndicator.setMaximumSize(QSize(20, 20))
        self.connectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout.addWidget(self.connectionIndicator)

        self.horizontalLayout_13.addLayout(self.horizontalLayout)

        self.horizontalSpacer_2 = QSpacerItem(275, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addWidget(self.connectBox)

        self.boxSettings = QGroupBox(self.groupBox_general)
        self.boxSettings.setObjectName("boxSettings")
        self.boxSettings.setEnabled(True)
        self.verticalLayout_3 = QVBoxLayout(self.boxSettings)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.lineEdit_Integ = QLineEdit(self.boxSettings)
        self.lineEdit_Integ.setObjectName("lineEdit_Integ")
        self.lineEdit_Integ.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_10.addWidget(self.lineEdit_Integ)

        self.integTimeText = QLabel(self.boxSettings)
        self.integTimeText.setObjectName("integTimeText")

        self.horizontalLayout_10.addWidget(self.integTimeText)

        self.secondText = QLabel(self.boxSettings)
        self.secondText.setObjectName("secondText")

        self.horizontalLayout_10.addWidget(self.secondText)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_4)

        self.setIntegrationTimeButton = QPushButton(self.boxSettings)
        self.setIntegrationTimeButton.setObjectName("setIntegrationTimeButton")
        self.setIntegrationTimeButton.setEnabled(False)

        self.horizontalLayout_10.addWidget(self.setIntegrationTimeButton)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_6)

        self.extTriggerCheck = QCheckBox(self.boxSettings)
        self.extTriggerCheck.setObjectName("extTriggerCheck")

        self.horizontalLayout_10.addWidget(self.extTriggerCheck)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer)

        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.getIntergrationTimelabel = QLabel(self.boxSettings)
        self.getIntergrationTimelabel.setObjectName("getIntergrationTimelabel")

        self.horizontalLayout_2.addWidget(self.getIntergrationTimelabel)

        self.getIntegrationTime_combo = QComboBox(self.boxSettings)
        self.getIntegrationTime_combo.addItem("")
        self.getIntegrationTime_combo.addItem("")
        self.getIntegrationTime_combo.setObjectName("getIntegrationTime_combo")

        self.horizontalLayout_2.addWidget(self.getIntegrationTime_combo)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_7)

        self.getTime_button = QPushButton(self.boxSettings)
        self.getTime_button.setObjectName("getTime_button")
        self.getTime_button.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.getTime_button)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_12)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 2)
        self.horizontalLayout_2.setStretch(3, 1)
        self.horizontalLayout_2.setStretch(4, 4)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.autoIntegrationTime_box = QGroupBox(self.boxSettings)
        self.autoIntegrationTime_box.setObjectName("autoIntegrationTime_box")
        self.horizontalLayout_11 = QHBoxLayout(self.autoIntegrationTime_box)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.autoIntegrationTIme_label = QLabel(self.autoIntegrationTime_box)
        self.autoIntegrationTIme_label.setObjectName("autoIntegrationTIme_label")

        self.horizontalLayout_11.addWidget(self.autoIntegrationTIme_label)

        self.useIntegrationTimeGuess_check = QCheckBox(self.autoIntegrationTime_box)
        self.useIntegrationTimeGuess_check.setObjectName("useIntegrationTimeGuess_check")

        self.horizontalLayout_11.addWidget(self.useIntegrationTimeGuess_check)

        self.saveAttempts_check = QCheckBox(self.autoIntegrationTime_box)
        self.saveAttempts_check.setObjectName("saveAttempts_check")

        self.horizontalLayout_11.addWidget(self.saveAttempts_check)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_11)

        self.verticalLayout_3.addWidget(self.autoIntegrationTime_box)

        self.verticalLayout.addWidget(self.boxSettings)

        self.previewBox = QGroupBox(self.groupBox_general)
        self.previewBox.setObjectName("previewBox")
        self.previewBox.setEnabled(False)
        self.horizontalLayout_3 = QHBoxLayout(self.previewBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.previewButton = QPushButton(self.previewBox)
        self.previewButton.setObjectName("previewButton")

        self.horizontalLayout_3.addWidget(self.previewButton)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.correctionCheck = QCheckBox(self.previewBox)
        self.correctionCheck.setObjectName("correctionCheck")

        self.horizontalLayout_3.addWidget(self.correctionCheck)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_8)

        self.verticalLayout.addWidget(self.previewBox)

        self.fileBox = QGroupBox(self.groupBox_general)
        self.fileBox.setObjectName("fileBox")
        self.fileBox.setEnabled(True)
        self.verticalLayout_2 = QVBoxLayout(self.fileBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pathLabel = QLabel(self.fileBox)
        self.pathLabel.setObjectName("pathLabel")
        self.pathLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_5.addWidget(self.pathLabel)

        self.lineEdit_path = QLineEdit(self.fileBox)
        self.lineEdit_path.setObjectName("lineEdit_path")

        self.horizontalLayout_5.addWidget(self.lineEdit_path)

        self.directoryButton = QPushButton(self.fileBox)
        self.directoryButton.setObjectName("directoryButton")

        self.horizontalLayout_5.addWidget(self.directoryButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.filenameLabel = QLabel(self.fileBox)
        self.filenameLabel.setObjectName("filenameLabel")
        self.filenameLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_6.addWidget(self.filenameLabel)

        self.lineEdit_filename = QLineEdit(self.fileBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.horizontalLayout_6.addWidget(self.lineEdit_filename)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_9)

        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.sampleName_label = QLabel(self.fileBox)
        self.sampleName_label.setObjectName("sampleName_label")
        self.sampleName_label.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_7.addWidget(self.sampleName_label)

        self.lineEdit_sampleName = QLineEdit(self.fileBox)
        self.lineEdit_sampleName.setObjectName("lineEdit_sampleName")

        self.horizontalLayout_7.addWidget(self.lineEdit_sampleName)

        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_comment = QLabel(self.fileBox)
        self.label_comment.setObjectName("label_comment")
        self.label_comment.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_8.addWidget(self.label_comment)

        self.lineEdit_comment = QLineEdit(self.fileBox)
        self.lineEdit_comment.setObjectName("lineEdit_comment")
        self.lineEdit_comment.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_8.addWidget(self.lineEdit_comment)

        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_10)

        self.saveButton = QPushButton(self.fileBox)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setEnabled(False)

        self.horizontalLayout_9.addWidget(self.saveButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.verticalLayout.addWidget(self.fileBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_5.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Template settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Thorlabs CCS settings", None))
        self.connectBox.setTitle("")
        self.connectButton.setText(QCoreApplication.translate("Form", "Connect", None))
        self.disconnectButton.setText(QCoreApplication.translate("Form", "Disconnect", None))
        self.label.setText(QCoreApplication.translate("Form", "Backend", None))
        self.statusLabel.setText(QCoreApplication.translate("Form", "Connection status", None))
        self.connectionIndicator.setText("")
        self.boxSettings.setTitle("")
        self.lineEdit_Integ.setText(QCoreApplication.translate("Form", "100", None))
        self.integTimeText.setText(QCoreApplication.translate("Form", "Integration time", None))
        self.secondText.setText(QCoreApplication.translate("Form", "ms", None))
        self.setIntegrationTimeButton.setText(QCoreApplication.translate("Form", "Set integration time", None))
        self.extTriggerCheck.setText(QCoreApplication.translate("Form", "use external trigger", None))
        self.getIntergrationTimelabel.setText(QCoreApplication.translate("Form", "Get integration time", None))
        self.getIntegrationTime_combo.setItemText(0, QCoreApplication.translate("Form", "manual", None))
        self.getIntegrationTime_combo.setItemText(1, QCoreApplication.translate("Form", "auto", None))

        self.getTime_button.setText(QCoreApplication.translate("Form", "get time", None))
        self.autoIntegrationTime_box.setTitle("")
        self.autoIntegrationTIme_label.setText(QCoreApplication.translate("Form", "Auto integrationtime options:", None))
        self.useIntegrationTimeGuess_check.setText(QCoreApplication.translate("Form", "use manual integration time as initial guess", None))
        self.saveAttempts_check.setText(QCoreApplication.translate("Form", "save attempts", None))
        self.previewBox.setTitle("")
        self.previewButton.setText(QCoreApplication.translate("Form", "preview", None))
        self.correctionCheck.setText(QCoreApplication.translate("Form", "use spectrum correction for preview", None))
        self.fileBox.setTitle("")
        self.pathLabel.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.filenameLabel.setText(QCoreApplication.translate("Form", "Filename", None))
        self.sampleName_label.setText(QCoreApplication.translate("Form", "Sample name", None))
        self.label_comment.setText(QCoreApplication.translate("Form", "Comment", None))
        self.saveButton.setText(QCoreApplication.translate("Form", "save", None))

    # retranslateUi
