################################################################################
## Form generated from reading UI file 'conDetect_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(868, 649)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 848, 629))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.controlBox = QGroupBox(self.groupBox_general)
        self.controlBox.setObjectName("controlBox")
        self.verticalLayout_4 = QVBoxLayout(self.controlBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.SourceLayout = QHBoxLayout()
        self.SourceLayout.setObjectName("SourceLayout")
        self.sourceText = QLabel(self.controlBox)
        self.sourceText.setObjectName("sourceText")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sourceText.sizePolicy().hasHeightForWidth())
        self.sourceText.setSizePolicy(sizePolicy1)
        self.sourceText.setMinimumSize(QSize(0, 0))

        self.SourceLayout.addWidget(self.sourceText)

        self.sourceLabel = QLabel(self.controlBox)
        self.sourceLabel.setObjectName("sourceLabel")

        self.SourceLayout.addWidget(self.sourceLabel)

        self.sourceLine = QLineEdit(self.controlBox)
        self.sourceLine.setObjectName("sourceLine")

        self.SourceLayout.addWidget(self.sourceLine)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SourceLayout.addItem(self.horizontalSpacer)

        self.SourceLayout.setStretch(0, 1)
        self.SourceLayout.setStretch(2, 1)
        self.SourceLayout.setStretch(3, 4)

        self.verticalLayout_4.addLayout(self.SourceLayout)

        self.SourceLayout_3 = QHBoxLayout()
        self.SourceLayout_3.setObjectName("SourceLayout_3")
        self.connectButton = QPushButton(self.controlBox)
        self.connectButton.setObjectName("connectButton")

        self.SourceLayout_3.addWidget(self.connectButton)

        self.disconnectButton = QPushButton(self.controlBox)
        self.disconnectButton.setObjectName("disconnectButton")
        self.disconnectButton.setEnabled(False)

        self.SourceLayout_3.addWidget(self.disconnectButton)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SourceLayout_3.addItem(self.horizontalSpacer_12)

        self.statusLabel_6 = QLabel(self.controlBox)
        self.statusLabel_6.setObjectName("statusLabel_6")

        self.SourceLayout_3.addWidget(self.statusLabel_6)

        self.connectionIndicator = QLabel(self.controlBox)
        self.connectionIndicator.setObjectName("connectionIndicator")
        self.connectionIndicator.setMaximumSize(QSize(20, 20))
        self.connectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.SourceLayout_3.addWidget(self.connectionIndicator)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SourceLayout_3.addItem(self.horizontalSpacer_13)

        self.verticalLayout_4.addLayout(self.SourceLayout_3)

        self.verticalLayout.addWidget(self.controlBox)

        self.statusBox = QGroupBox(self.groupBox_general)
        self.statusBox.setObjectName("statusBox")
        self.statusBox.setEnabled(False)
        self.verticalLayout_5 = QVBoxLayout(self.statusBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.hiConnectLayout = QHBoxLayout()
        self.hiConnectLayout.setObjectName("hiConnectLayout")
        self.hiConnectionButton = QPushButton(self.statusBox)
        self.hiConnectionButton.setObjectName("hiConnectionButton")

        self.hiConnectLayout.addWidget(self.hiConnectionButton)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hiConnectLayout.addItem(self.horizontalSpacer_5)

        self.statusLabel_2 = QLabel(self.statusBox)
        self.statusLabel_2.setObjectName("statusLabel_2")
        self.statusLabel_2.setMinimumSize(QSize(140, 0))
        self.statusLabel_2.setMaximumSize(QSize(150, 16777215))

        self.hiConnectLayout.addWidget(self.statusLabel_2)

        self.hiConnectionIndicator = QLabel(self.statusBox)
        self.hiConnectionIndicator.setObjectName("hiConnectionIndicator")
        self.hiConnectionIndicator.setMaximumSize(QSize(20, 20))
        self.hiConnectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.hiConnectLayout.addWidget(self.hiConnectionIndicator)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hiConnectLayout.addItem(self.horizontalSpacer_3)

        self.verticalLayout_5.addLayout(self.hiConnectLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.loConnectionButton = QPushButton(self.statusBox)
        self.loConnectionButton.setObjectName("loConnectionButton")

        self.horizontalLayout_3.addWidget(self.loConnectionButton)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_9)

        self.statusLabel_4 = QLabel(self.statusBox)
        self.statusLabel_4.setObjectName("statusLabel_4")
        self.statusLabel_4.setMinimumSize(QSize(140, 0))
        self.statusLabel_4.setMaximumSize(QSize(150, 16777215))

        self.horizontalLayout_3.addWidget(self.statusLabel_4)

        self.loConnectionIndicator = QLabel(self.statusBox)
        self.loConnectionIndicator.setObjectName("loConnectionIndicator")
        self.loConnectionIndicator.setMaximumSize(QSize(20, 20))
        self.loConnectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_3.addWidget(self.loConnectionIndicator)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_10)

        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.verticalLayout.addWidget(self.statusBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Connection check settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Connection detector", None))
        self.controlBox.setTitle(QCoreApplication.translate("Form", "Multiplexor control", None))
        self.sourceText.setText(QCoreApplication.translate("Form", "Multiplexor:", None))
        self.sourceLabel.setText(QCoreApplication.translate("Form", "source", None))
        self.sourceLine.setText(QCoreApplication.translate("Form", "/dev/ttyUSB1", None))
        self.connectButton.setText(QCoreApplication.translate("Form", "Connect", None))
        self.disconnectButton.setText(QCoreApplication.translate("Form", "Disconnect", None))
        self.statusLabel_6.setText(QCoreApplication.translate("Form", "Multiplexor connected", None))
        self.connectionIndicator.setText("")
        self.statusBox.setTitle(QCoreApplication.translate("Form", "Check", None))
        self.hiConnectionButton.setText(QCoreApplication.translate("Form", "Hi check", None))
        self.statusLabel_2.setText(QCoreApplication.translate("Form", "Hi & HiSence check", None))
        self.hiConnectionIndicator.setText("")
        self.loConnectionButton.setText(QCoreApplication.translate("Form", "Lo check", None))
        self.statusLabel_4.setText(QCoreApplication.translate("Form", "Lo & LoSence check", None))
        self.loConnectionIndicator.setText("")

    # retranslateUi
