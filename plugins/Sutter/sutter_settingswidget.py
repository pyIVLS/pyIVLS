################################################################################
## Form generated from reading UI file 'Sutter_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1269, 773)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1249, 753))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sourceText = QLabel(self.scrollAreaWidgetContents)
        self.sourceText.setObjectName("sourceText")

        self.horizontalLayout.addWidget(self.sourceText)

        self.sourceInput = QLineEdit(self.scrollAreaWidgetContents)
        self.sourceInput.setObjectName("sourceInput")

        self.horizontalLayout.addWidget(self.sourceInput)

        self.horizontalLayout_4.addLayout(self.horizontalLayout)

        self.connectButton = QPushButton(self.scrollAreaWidgetContents)
        self.connectButton.setObjectName("connectButton")

        self.horizontalLayout_4.addWidget(self.connectButton)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_10.addWidget(self.label_5)

        self.backend_combo = QComboBox(self.scrollAreaWidgetContents)
        self.backend_combo.setObjectName("backend_combo")

        self.horizontalLayout_10.addWidget(self.backend_combo)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName("label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label)

        self.connectionIndicator = QLabel(self.scrollAreaWidgetContents)
        self.connectionIndicator.setObjectName("connectionIndicator")
        self.connectionIndicator.setMaximumSize(QSize(20, 20))
        self.connectionIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_3.addWidget(self.connectionIndicator)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.basicBox = QGroupBox(self.scrollAreaWidgetContents)
        self.basicBox.setObjectName("basicBox")
        self.horizontalLayout_2 = QHBoxLayout(self.basicBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibrateButton = QPushButton(self.basicBox)
        self.calibrateButton.setObjectName("calibrateButton")

        self.horizontalLayout_2.addWidget(self.calibrateButton)

        self.stopButton = QPushButton(self.basicBox)
        self.stopButton.setObjectName("stopButton")

        self.horizontalLayout_2.addWidget(self.stopButton)

        self.verticalLayout_2.addWidget(self.basicBox)

        self.settingsBox = QGroupBox(self.scrollAreaWidgetContents)
        self.settingsBox.setObjectName("settingsBox")
        self.horizontalLayout_8 = QHBoxLayout(self.settingsBox)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.checkBox_segment = QCheckBox(self.settingsBox)
        self.checkBox_segment.setObjectName("checkBox_segment")

        self.horizontalLayout_9.addWidget(self.checkBox_segment)

        self.spinBox_seglength = QSpinBox(self.settingsBox)
        self.spinBox_seglength.setObjectName("spinBox_seglength")
        self.spinBox_seglength.setMinimum(1)
        self.spinBox_seglength.setMaximum(25000)

        self.horizontalLayout_9.addWidget(self.spinBox_seglength)

        self.label_4 = QLabel(self.settingsBox)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_9.addWidget(self.label_4)

        self.horizontalLayout_8.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.quickBox = QCheckBox(self.settingsBox)
        self.quickBox.setObjectName("quickBox")

        self.horizontalLayout_7.addWidget(self.quickBox)

        self.speedText = QLabel(self.settingsBox)
        self.speedText.setObjectName("speedText")
        self.speedText.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.speedText)

        self.speedComboBox = QComboBox(self.settingsBox)
        self.speedComboBox.setObjectName("speedComboBox")

        self.horizontalLayout_7.addWidget(self.speedComboBox)

        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QLabel(self.settingsBox)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.devnumCombo = QComboBox(self.settingsBox)
        self.devnumCombo.setObjectName("devnumCombo")

        self.horizontalLayout_6.addWidget(self.devnumCombo)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_3 = QLabel(self.settingsBox)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_5.addWidget(self.label_3)

        self.functionCombo = QComboBox(self.settingsBox)
        self.functionCombo.setObjectName("functionCombo")

        self.horizontalLayout_5.addWidget(self.functionCombo)

        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_8.addLayout(self.verticalLayout)

        self.verticalLayout_2.addWidget(self.settingsBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Sutter settings", None))
        self.sourceText.setText(QCoreApplication.translate("Form", "Source:", None))
        self.sourceInput.setText("")
        self.connectButton.setText(QCoreApplication.translate("Form", "Connect", None))
        self.label_5.setText(QCoreApplication.translate("Form", "Backend", None))
        self.label.setText(QCoreApplication.translate("Form", "Connection status", None))
        self.connectionIndicator.setText("")
        self.basicBox.setTitle(QCoreApplication.translate("Form", "Basic functionality", None))
        self.calibrateButton.setText(QCoreApplication.translate("Form", "Calibrate", None))
        self.stopButton.setText(QCoreApplication.translate("Form", "Stop", None))
        self.settingsBox.setTitle(QCoreApplication.translate("Form", "Settings:", None))
        self.checkBox_segment.setText(QCoreApplication.translate("Form", "Segment moves", None))
        self.label_4.setText(QCoreApplication.translate("Form", "microns", None))
        self.quickBox.setText(QCoreApplication.translate("Form", "Quickmove", None))
        self.speedText.setText(QCoreApplication.translate("Form", "movement speed", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Micromanipulator number", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Micromanipulator function", None))

    # retranslateUi
