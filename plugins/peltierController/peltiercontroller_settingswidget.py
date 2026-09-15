################################################################################
## Form generated from reading UI file 'peltierController_settingsWidget.ui'
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
        Form.resize(826, 613)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 806, 593))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.sourceBox = QGroupBox(self.groupBox_general)
        self.sourceBox.setObjectName("sourceBox")
        self.horizontalLayout = QHBoxLayout(self.sourceBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sourceText = QLabel(self.sourceBox)
        self.sourceText.setObjectName("sourceText")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sourceText.sizePolicy().hasHeightForWidth())
        self.sourceText.setSizePolicy(sizePolicy1)
        self.sourceText.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.sourceText)

        self.peltierSource = QLineEdit(self.sourceBox)
        self.peltierSource.setObjectName("peltierSource")

        self.horizontalLayout.addWidget(self.peltierSource)

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

        self.connectButton = QPushButton(self.sourceBox)
        self.connectButton.setObjectName("connectButton")

        self.horizontalLayout.addWidget(self.connectButton)

        self.disconnectButton = QPushButton(self.sourceBox)
        self.disconnectButton.setObjectName("disconnectButton")
        self.disconnectButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.disconnectButton)

        self.verticalLayout.addWidget(self.sourceBox)

        self.settingsGroupBox = QGroupBox(self.groupBox_general)
        self.settingsGroupBox.setObjectName("settingsGroupBox")
        self.settingsGroupBox.setEnabled(False)
        self.horizontalLayout_2 = QHBoxLayout(self.settingsGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.setTEdit = QLineEdit(self.settingsGroupBox)
        self.setTEdit.setObjectName("setTEdit")

        self.horizontalLayout_2.addWidget(self.setTEdit)

        self.setTUnitsLabel = QLabel(self.settingsGroupBox)
        self.setTUnitsLabel.setObjectName("setTUnitsLabel")

        self.horizontalLayout_2.addWidget(self.setTUnitsLabel)

        self.setTButton = QPushButton(self.settingsGroupBox)
        self.setTButton.setObjectName("setTButton")
        self.setTButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.setTButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.setPEdit = QLineEdit(self.settingsGroupBox)
        self.setPEdit.setObjectName("setPEdit")

        self.horizontalLayout_2.addWidget(self.setPEdit)

        self.setPLabel = QLabel(self.settingsGroupBox)
        self.setPLabel.setObjectName("setPLabel")

        self.horizontalLayout_2.addWidget(self.setPLabel)

        self.setPButton = QPushButton(self.settingsGroupBox)
        self.setPButton.setObjectName("setPButton")
        self.setPButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.setPButton)

        self.verticalLayout.addWidget(self.settingsGroupBox)

        self.DisplayGroupBox = QGroupBox(self.groupBox_general)
        self.DisplayGroupBox.setObjectName("DisplayGroupBox")
        self.DisplayGroupBox.setEnabled(False)
        self.horizontalLayout_3 = QHBoxLayout(self.DisplayGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.periodLabel = QLabel(self.DisplayGroupBox)
        self.periodLabel.setObjectName("periodLabel")
        self.periodLabel.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_3.addWidget(self.periodLabel)

        self.periodEdit = QLineEdit(self.DisplayGroupBox)
        self.periodEdit.setObjectName("periodEdit")

        self.horizontalLayout_3.addWidget(self.periodEdit)

        self.periodUnitsLabel = QLabel(self.DisplayGroupBox)
        self.periodUnitsLabel.setObjectName("periodUnitsLabel")

        self.horizontalLayout_3.addWidget(self.periodUnitsLabel)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.periodDisplayLabel = QLabel(self.DisplayGroupBox)
        self.periodDisplayLabel.setObjectName("periodDisplayLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.periodDisplayLabel.sizePolicy().hasHeightForWidth())
        self.periodDisplayLabel.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.periodDisplayLabel)

        self.periodPtsEdit = QLineEdit(self.DisplayGroupBox)
        self.periodPtsEdit.setObjectName("periodPtsEdit")

        self.horizontalLayout_3.addWidget(self.periodPtsEdit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.periodCheck = QPushButton(self.DisplayGroupBox)
        self.periodCheck.setObjectName("periodCheck")
        self.periodCheck.setMinimumSize(QSize(100, 0))
        self.periodCheck.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.periodCheck)

        self.verticalLayout.addWidget(self.DisplayGroupBox)

        self.PIDbox = QGroupBox(self.groupBox_general)
        self.PIDbox.setObjectName("PIDbox")
        self.PIDbox.setEnabled(False)
        self.horizontalLayout_5 = QHBoxLayout(self.PIDbox)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.KPlabel = QLabel(self.PIDbox)
        self.KPlabel.setObjectName("KPlabel")

        self.horizontalLayout_5.addWidget(self.KPlabel)

        self.KPlineEdit = QLineEdit(self.PIDbox)
        self.KPlineEdit.setObjectName("KPlineEdit")

        self.horizontalLayout_5.addWidget(self.KPlineEdit)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_9)

        self.KIlabel = QLabel(self.PIDbox)
        self.KIlabel.setObjectName("KIlabel")

        self.horizontalLayout_5.addWidget(self.KIlabel)

        self.KIlineEdit = QLineEdit(self.PIDbox)
        self.KIlineEdit.setObjectName("KIlineEdit")

        self.horizontalLayout_5.addWidget(self.KIlineEdit)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_10)

        self.KDlabel = QLabel(self.PIDbox)
        self.KDlabel.setObjectName("KDlabel")

        self.horizontalLayout_5.addWidget(self.KDlabel)

        self.KDlineEdit = QLineEdit(self.PIDbox)
        self.KDlineEdit.setObjectName("KDlineEdit")

        self.horizontalLayout_5.addWidget(self.KDlineEdit)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_11)

        self.PIDbutton = QPushButton(self.PIDbox)
        self.PIDbutton.setObjectName("PIDbutton")

        self.horizontalLayout_5.addWidget(self.PIDbutton)

        self.verticalLayout.addWidget(self.PIDbox)

        self.groupBox_3 = QGroupBox(self.groupBox_general)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sweepStartLabel = QLabel(self.groupBox_3)
        self.sweepStartLabel.setObjectName("sweepStartLabel")

        self.horizontalLayout_4.addWidget(self.sweepStartLabel)

        self.sweepStartEdit = QLineEdit(self.groupBox_3)
        self.sweepStartEdit.setObjectName("sweepStartEdit")
        self.sweepStartEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepStartEdit)

        self.sweepStartUnitsLabel = QLabel(self.groupBox_3)
        self.sweepStartUnitsLabel.setObjectName("sweepStartUnitsLabel")

        self.horizontalLayout_4.addWidget(self.sweepStartUnitsLabel)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.sweepEndLabel = QLabel(self.groupBox_3)
        self.sweepEndLabel.setObjectName("sweepEndLabel")

        self.horizontalLayout_4.addWidget(self.sweepEndLabel)

        self.sweepEndEdit = QLineEdit(self.groupBox_3)
        self.sweepEndEdit.setObjectName("sweepEndEdit")
        self.sweepEndEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepEndEdit)

        self.sweepEndUnitsLabel = QLabel(self.groupBox_3)
        self.sweepEndUnitsLabel.setObjectName("sweepEndUnitsLabel")

        self.horizontalLayout_4.addWidget(self.sweepEndUnitsLabel)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.sweepStepLabel = QLabel(self.groupBox_3)
        self.sweepStepLabel.setObjectName("sweepStepLabel")

        self.horizontalLayout_4.addWidget(self.sweepStepLabel)

        self.sweepPtsEdit = QLineEdit(self.groupBox_3)
        self.sweepPtsEdit.setObjectName("sweepPtsEdit")
        self.sweepPtsEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepPtsEdit)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.sweepStabilizationLabel = QLabel(self.groupBox_3)
        self.sweepStabilizationLabel.setObjectName("sweepStabilizationLabel")

        self.horizontalLayout_4.addWidget(self.sweepStabilizationLabel)

        self.sweepStabilizationEdit = QLineEdit(self.groupBox_3)
        self.sweepStabilizationEdit.setObjectName("sweepStabilizationEdit")
        self.sweepStabilizationEdit.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepStabilizationEdit)

        self.sweepStabilizationUnitLabel = QLabel(self.groupBox_3)
        self.sweepStabilizationUnitLabel.setObjectName("sweepStabilizationUnitLabel")

        self.horizontalLayout_4.addWidget(self.sweepStabilizationUnitLabel)

        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Pelteir controller settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Peltier controller settings", None))
        self.sourceBox.setTitle(QCoreApplication.translate("Form", "Connection", None))
        self.sourceText.setText(QCoreApplication.translate("Form", "Source", None))
        self.peltierSource.setText(QCoreApplication.translate("Form", "/dev/ttyUSB0", None))
        self.statusLabel.setText(QCoreApplication.translate("Form", "Connection status", None))
        self.sourceLabel.setText("")
        self.connectionIndicator.setText("")
        self.connectButton.setText(QCoreApplication.translate("Form", "Connect", None))
        self.disconnectButton.setText(QCoreApplication.translate("Form", "Disconnect", None))
        self.settingsGroupBox.setTitle(QCoreApplication.translate("Form", "Manual settings", None))
        self.setTEdit.setText(QCoreApplication.translate("Form", "22", None))
        self.setTUnitsLabel.setText(QCoreApplication.translate("Form", '<html><head/><body><p><span style=" vertical-align:super;">o</span>C</p></body></html>', None))
        self.setTButton.setText(QCoreApplication.translate("Form", "set temperature", None))
        self.setPEdit.setText(QCoreApplication.translate("Form", "0", None))
        self.setPLabel.setText(QCoreApplication.translate("Form", "% of full power", None))
        self.setPButton.setText(QCoreApplication.translate("Form", "set power", None))
        self.DisplayGroupBox.setTitle(QCoreApplication.translate("Form", "Display", None))
        self.periodLabel.setText(QCoreApplication.translate("Form", "Check period", None))
        self.periodEdit.setText(QCoreApplication.translate("Form", "10", None))
        self.periodUnitsLabel.setText(QCoreApplication.translate("Form", "s", None))
        self.periodDisplayLabel.setText(QCoreApplication.translate("Form", "Points to show", None))
        self.periodPtsEdit.setText(QCoreApplication.translate("Form", "10", None))
        self.periodCheck.setText(QCoreApplication.translate("Form", "Start check", None))
        self.PIDbox.setTitle(QCoreApplication.translate("Form", "PID parameters", None))
        self.KPlabel.setText(QCoreApplication.translate("Form", "Kp", None))
        self.KIlabel.setText(QCoreApplication.translate("Form", "Ki", None))
        self.KDlabel.setText(QCoreApplication.translate("Form", "Kd", None))
        self.PIDbutton.setText(QCoreApplication.translate("Form", "Set PID", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", "Sweep", None))
        self.sweepStartLabel.setText(QCoreApplication.translate("Form", "Start", None))
        self.sweepStartEdit.setText(QCoreApplication.translate("Form", "10", None))
        self.sweepStartUnitsLabel.setText(QCoreApplication.translate("Form", '<html><head/><body><p><span style=" vertical-align:super;">o</span>C</p></body></html>', None))
        self.sweepEndLabel.setText(QCoreApplication.translate("Form", "End", None))
        self.sweepEndEdit.setText(QCoreApplication.translate("Form", "40", None))
        self.sweepEndUnitsLabel.setText(QCoreApplication.translate("Form", '<html><head/><body><p><span style=" vertical-align:super;">o</span>C</p></body></html>', None))
        self.sweepStepLabel.setText(QCoreApplication.translate("Form", "Points", None))
        self.sweepPtsEdit.setText(QCoreApplication.translate("Form", "4", None))
        self.sweepStabilizationLabel.setText(QCoreApplication.translate("Form", "Stabilization time", None))
        self.sweepStabilizationEdit.setText("")
        self.sweepStabilizationUnitLabel.setText(QCoreApplication.translate("Form", "s", None))

    # retranslateUi
