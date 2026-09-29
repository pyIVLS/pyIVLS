################################################################################
## Form generated from reading UI file 'itc503_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtWidgets import QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(826, 687)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 806, 667))
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

        self.source = QLineEdit(self.sourceBox)
        self.source.setObjectName("source")

        self.horizontalLayout.addWidget(self.source)

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
        self.setTEdit.setMaximumSize(QSize(120, 16777215))

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
        self.periodCheck.setMinimumSize(QSize(120, 0))
        self.periodCheck.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.periodCheck)

        self.verticalLayout.addWidget(self.DisplayGroupBox)

        self.groupBox_3 = QGroupBox(self.groupBox_general)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sweepStartLabel = QLabel(self.groupBox_3)
        self.sweepStartLabel.setObjectName("sweepStartLabel")

        self.horizontalLayout_4.addWidget(self.sweepStartLabel)

        self.sweepStartEdit = QLineEdit(self.groupBox_3)
        self.sweepStartEdit.setObjectName("sweepStartEdit")
        self.sweepStartEdit.setMinimumSize(QSize(50, 0))
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
        self.sweepEndEdit.setMinimumSize(QSize(50, 0))
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
        self.sweepPtsEdit.setMinimumSize(QSize(50, 0))
        self.sweepPtsEdit.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepPtsEdit)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.sweepStabilizationLabel = QLabel(self.groupBox_3)
        self.sweepStabilizationLabel.setObjectName("sweepStabilizationLabel")

        self.horizontalLayout_4.addWidget(self.sweepStabilizationLabel)

        self.sweepStabilizationEdit = QLineEdit(self.groupBox_3)
        self.sweepStabilizationEdit.setObjectName("sweepStabilizationEdit")
        self.sweepStabilizationEdit.setMinimumSize(QSize(90, 0))
        self.sweepStabilizationEdit.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_4.addWidget(self.sweepStabilizationEdit)

        self.sweepStabilizationUnitLabel = QLabel(self.groupBox_3)
        self.sweepStabilizationUnitLabel.setObjectName("sweepStabilizationUnitLabel")

        self.horizontalLayout_4.addWidget(self.sweepStabilizationUnitLabel)

        self.verticalLayout.addWidget(self.groupBox_3)

        self.logBox = QGroupBox(self.groupBox_general)
        self.logBox.setObjectName("logBox")
        self.horizontalLayout_5 = QHBoxLayout(self.logBox)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.logCheckBox = QCheckBox(self.logBox)
        self.logCheckBox.setObjectName("logCheckBox")
        self.logCheckBox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_5.addWidget(self.logCheckBox)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_11)

        self.logWholeBox = QCheckBox(self.logBox)
        self.logWholeBox.setObjectName("logWholeBox")
        self.logWholeBox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_5.addWidget(self.logWholeBox)

        self.verticalLayout.addWidget(self.logBox)

        self.saveBox = QGroupBox(self.groupBox_general)
        self.saveBox.setObjectName("saveBox")
        self.gridLayout_3 = QGridLayout(self.saveBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.fileNameLine = QLineEdit(self.saveBox)
        self.fileNameLine.setObjectName("fileNameLine")

        self.gridLayout_3.addWidget(self.fileNameLine, 1, 2, 1, 1)

        self.directoryButton = QPushButton(self.saveBox)
        self.directoryButton.setObjectName("directoryButton")

        self.gridLayout_3.addWidget(self.directoryButton, 0, 3, 1, 1)

        self.label_3 = QLabel(self.saveBox)
        self.label_3.setObjectName("label_3")

        self.gridLayout_3.addWidget(self.label_3, 1, 1, 1, 1)

        self.addressLine = QLineEdit(self.saveBox)
        self.addressLine.setObjectName("addressLine")

        self.gridLayout_3.addWidget(self.addressLine, 0, 2, 1, 1)

        self.label_2 = QLabel(self.saveBox)
        self.label_2.setObjectName("label_2")

        self.gridLayout_3.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_5 = QLabel(self.saveBox)
        self.label_5.setObjectName("label_5")

        self.gridLayout_3.addWidget(self.label_5, 3, 1, 1, 1)

        self.sampleNameLine = QLineEdit(self.saveBox)
        self.sampleNameLine.setObjectName("sampleNameLine")

        self.gridLayout_3.addWidget(self.sampleNameLine, 2, 2, 1, 1)

        self.label = QLabel(self.saveBox)
        self.label.setObjectName("label")

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.saveButton = QPushButton(self.saveBox)
        self.saveButton.setObjectName("saveButton")

        self.gridLayout_3.addWidget(self.saveButton, 1, 3, 1, 1)

        self.label_4 = QLabel(self.saveBox)
        self.label_4.setObjectName("label_4")

        self.gridLayout_3.addWidget(self.label_4, 2, 1, 1, 1)

        self.commentLine = QLineEdit(self.saveBox)
        self.commentLine.setObjectName("commentLine")

        self.gridLayout_3.addWidget(self.commentLine, 3, 2, 1, 1)

        self.stopLogButton = QPushButton(self.saveBox)
        self.stopLogButton.setObjectName("stopLogButton")

        self.gridLayout_3.addWidget(self.stopLogButton, 2, 3, 1, 1)

        self.verticalLayout.addWidget(self.saveBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "itc503 controller settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Peltier controller settings", None))
        self.sourceBox.setTitle(QCoreApplication.translate("Form", "Connection", None))
        self.sourceText.setText(QCoreApplication.translate("Form", "Source", None))
        self.source.setText("")
        self.statusLabel.setText(QCoreApplication.translate("Form", "Connection status", None))
        self.sourceLabel.setText("")
        self.connectionIndicator.setText("")
        self.connectButton.setText(QCoreApplication.translate("Form", "Connect", None))
        self.disconnectButton.setText(QCoreApplication.translate("Form", "Disconnect", None))
        self.settingsGroupBox.setTitle(QCoreApplication.translate("Form", "Manual settings", None))
        self.setTEdit.setText("")
        self.setTUnitsLabel.setText(QCoreApplication.translate("Form", '<html><head/><body><p><span style=" vertical-align:super;">o</span>C</p></body></html>', None))
        self.setTButton.setText(QCoreApplication.translate("Form", "set temperature", None))
        self.DisplayGroupBox.setTitle(QCoreApplication.translate("Form", "Check/Log", None))
        self.periodLabel.setText(QCoreApplication.translate("Form", "Check period", None))
        self.periodEdit.setText("")
        self.periodUnitsLabel.setText(QCoreApplication.translate("Form", "s", None))
        self.periodDisplayLabel.setText(QCoreApplication.translate("Form", "Time to show", None))
        self.periodPtsEdit.setText("")
        self.periodCheck.setText(QCoreApplication.translate("Form", "Start check", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", "Sweep", None))
        self.sweepStartLabel.setText(QCoreApplication.translate("Form", "Start", None))
        self.sweepStartEdit.setText("")
        self.sweepStartUnitsLabel.setText(QCoreApplication.translate("Form", "<html><head/><body><p>K</p></body></html>", None))
        self.sweepEndLabel.setText(QCoreApplication.translate("Form", "End", None))
        self.sweepEndEdit.setText("")
        self.sweepEndUnitsLabel.setText(QCoreApplication.translate("Form", "<html><head/><body><p>K</p></body></html>", None))
        self.sweepStepLabel.setText(QCoreApplication.translate("Form", "Points", None))
        self.sweepPtsEdit.setText("")
        self.sweepStabilizationLabel.setText(QCoreApplication.translate("Form", "Stabilization time", None))
        self.sweepStabilizationEdit.setText("")
        self.sweepStabilizationUnitLabel.setText(QCoreApplication.translate("Form", "s", None))
        self.logBox.setTitle(QCoreApplication.translate("Form", "Temperature log", None))
        self.logCheckBox.setText(QCoreApplication.translate("Form", "Log", None))
        self.logWholeBox.setText(QCoreApplication.translate("Form", "Whole experiment", None))
        self.saveBox.setTitle(QCoreApplication.translate("Form", "Save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Filename", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.label_5.setText(QCoreApplication.translate("Form", "Comment", None))
        self.label.setText("")
        self.saveButton.setText(QCoreApplication.translate("Form", "Save", None))
        self.label_4.setText(QCoreApplication.translate("Form", "Sample name", None))
        self.stopLogButton.setText(QCoreApplication.translate("Form", "Stop logging", None))

    # retranslateUi
