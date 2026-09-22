################################################################################
## Form generated from reading UI file 'timeIV_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(869, 722)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 849, 702))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QGroupBox(self.groupBox_general)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.smuBox = QComboBox(self.groupBox_2)
        self.smuBox.setObjectName("smuBox")

        self.gridLayout_2.addWidget(self.smuBox, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self.groupBox_general)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.stepLabel = QLabel(self.groupBox)
        self.stepLabel.setObjectName("stepLabel")

        self.horizontalLayout_3.addWidget(self.stepLabel)

        self.step_lineEdit = QLineEdit(self.groupBox)
        self.step_lineEdit.setObjectName("step_lineEdit")
        self.step_lineEdit.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.step_lineEdit)

        self.stepUnitsLabel = QLabel(self.groupBox)
        self.stepUnitsLabel.setObjectName("stepUnitsLabel")

        self.horizontalLayout_3.addWidget(self.stepUnitsLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.stopTimerCheckBox = QCheckBox(self.groupBox)
        self.stopTimerCheckBox.setObjectName("stopTimerCheckBox")

        self.horizontalLayout_3.addWidget(self.stopTimerCheckBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.stopAfterlabel = QLabel(self.groupBox)
        self.stopAfterlabel.setObjectName("stopAfterlabel")
        self.stopAfterlabel.setFrameShape(QFrame.Shape.NoFrame)

        self.horizontalLayout_3.addWidget(self.stopAfterlabel)

        self.stopAfterLineEdit = QLineEdit(self.groupBox)
        self.stopAfterLineEdit.setObjectName("stopAfterLineEdit")

        self.horizontalLayout_3.addWidget(self.stopAfterLineEdit)

        self.stopAfteUnitslabel = QLabel(self.groupBox)
        self.stopAfteUnitslabel.setObjectName("stopAfteUnitslabel")

        self.horizontalLayout_3.addWidget(self.stopAfteUnitslabel)

        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_SMUGeneral = QGroupBox(self.groupBox_general)
        self.groupBox_SMUGeneral.setObjectName("groupBox_SMUGeneral")
        self.groupBox_SMUGeneral.setMinimumSize(QSize(0, 0))
        self.groupBox_SMUGeneral.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_SMUGeneral)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.SourceBox = QGroupBox(self.groupBox_SMUGeneral)
        self.SourceBox.setObjectName("SourceBox")
        self.verticalLayout_6 = QVBoxLayout(self.SourceBox)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.HBoxLayout_general = QHBoxLayout()
        self.HBoxLayout_general.setObjectName("HBoxLayout_general")
        self.HBoxLayout_channel = QHBoxLayout()
        self.HBoxLayout_channel.setObjectName("HBoxLayout_channel")
        self.label_Channel = QLabel(self.SourceBox)
        self.label_Channel.setObjectName("label_Channel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_Channel.sizePolicy().hasHeightForWidth())
        self.label_Channel.setSizePolicy(sizePolicy1)
        self.label_Channel.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_channel.addWidget(self.label_Channel)

        self.comboBox_channel = QComboBox(self.SourceBox)
        self.comboBox_channel.setObjectName("comboBox_channel")
        sizePolicy1.setHeightForWidth(self.comboBox_channel.sizePolicy().hasHeightForWidth())
        self.comboBox_channel.setSizePolicy(sizePolicy1)
        self.comboBox_channel.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_channel.addWidget(self.comboBox_channel)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_channel)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_general.addItem(self.horizontalSpacer_8)

        self.HBoxLayout_inject = QHBoxLayout()
        self.HBoxLayout_inject.setObjectName("HBoxLayout_inject")
        self.label_inject = QLabel(self.SourceBox)
        self.label_inject.setObjectName("label_inject")
        sizePolicy1.setHeightForWidth(self.label_inject.sizePolicy().hasHeightForWidth())
        self.label_inject.setSizePolicy(sizePolicy1)
        self.label_inject.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_inject.addWidget(self.label_inject)

        self.comboBox_inject = QComboBox(self.SourceBox)
        self.comboBox_inject.addItem("")
        self.comboBox_inject.addItem("")
        self.comboBox_inject.setObjectName("comboBox_inject")
        sizePolicy1.setHeightForWidth(self.comboBox_inject.sizePolicy().hasHeightForWidth())
        self.comboBox_inject.setSizePolicy(sizePolicy1)
        self.comboBox_inject.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_inject.addWidget(self.comboBox_inject)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_inject)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_general.addItem(self.horizontalSpacer_9)

        self.HBoxLayout_sourceSenseMode = QHBoxLayout()
        self.HBoxLayout_sourceSenseMode.setObjectName("HBoxLayout_sourceSenseMode")
        self.label_sourceSenseMode = QLabel(self.SourceBox)
        self.label_sourceSenseMode.setObjectName("label_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.label_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.label_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.label_sourceSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.label_sourceSenseMode)

        self.comboBox_sourceSenseMode = QComboBox(self.SourceBox)
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.setObjectName("comboBox_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.comboBox_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.comboBox_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.comboBox_sourceSenseMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.comboBox_sourceSenseMode)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_sourceSenseMode)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_general.addItem(self.horizontalSpacer_11)

        self.HBoxLayout_general.setStretch(0, 10)
        self.HBoxLayout_general.setStretch(1, 1)
        self.HBoxLayout_general.setStretch(2, 10)
        self.HBoxLayout_general.setStretch(3, 1)
        self.HBoxLayout_general.setStretch(5, 20)

        self.verticalLayout_6.addLayout(self.HBoxLayout_general)

        self.HBoxLayout_sourceLine2 = QHBoxLayout()
        self.HBoxLayout_sourceLine2.setObjectName("HBoxLayout_sourceLine2")
        self.HBoxLayout_sourceStart = QHBoxLayout()
        self.HBoxLayout_sourceStart.setObjectName("HBoxLayout_sourceStart")
        self.label_sourceSetValue = QLabel(self.SourceBox)
        self.label_sourceSetValue.setObjectName("label_sourceSetValue")
        sizePolicy1.setHeightForWidth(self.label_sourceSetValue.sizePolicy().hasHeightForWidth())
        self.label_sourceSetValue.setSizePolicy(sizePolicy1)
        self.label_sourceSetValue.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_sourceStart.addWidget(self.label_sourceSetValue)

        self.lineEdit_sourceSetValue = QLineEdit(self.SourceBox)
        self.lineEdit_sourceSetValue.setObjectName("lineEdit_sourceSetValue")
        sizePolicy1.setHeightForWidth(self.lineEdit_sourceSetValue.sizePolicy().hasHeightForWidth())
        self.lineEdit_sourceSetValue.setSizePolicy(sizePolicy1)
        self.lineEdit_sourceSetValue.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_sourceStart.addWidget(self.lineEdit_sourceSetValue)

        self.label_sourceSetValueUnits = QLabel(self.SourceBox)
        self.label_sourceSetValueUnits.setObjectName("label_sourceSetValueUnits")

        self.HBoxLayout_sourceStart.addWidget(self.label_sourceSetValueUnits)

        self.HBoxLayout_sourceLine2.addLayout(self.HBoxLayout_sourceStart)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceLine2.addItem(self.horizontalSpacer_7)

        self.HBoxLayout_sourceLimit = QHBoxLayout()
        self.HBoxLayout_sourceLimit.setObjectName("HBoxLayout_sourceLimit")
        self.label_sourceLimit = QLabel(self.SourceBox)
        self.label_sourceLimit.setObjectName("label_sourceLimit")
        sizePolicy1.setHeightForWidth(self.label_sourceLimit.sizePolicy().hasHeightForWidth())
        self.label_sourceLimit.setSizePolicy(sizePolicy1)
        self.label_sourceLimit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceLimit.addWidget(self.label_sourceLimit)

        self.lineEdit_sourceLimit = QLineEdit(self.SourceBox)
        self.lineEdit_sourceLimit.setObjectName("lineEdit_sourceLimit")
        sizePolicy1.setHeightForWidth(self.lineEdit_sourceLimit.sizePolicy().hasHeightForWidth())
        self.lineEdit_sourceLimit.setSizePolicy(sizePolicy1)
        self.lineEdit_sourceLimit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_sourceLimit.addWidget(self.lineEdit_sourceLimit)

        self.label_sourceLimitUnits = QLabel(self.SourceBox)
        self.label_sourceLimitUnits.setObjectName("label_sourceLimitUnits")

        self.HBoxLayout_sourceLimit.addWidget(self.label_sourceLimitUnits)

        self.HBoxLayout_sourceLine2.addLayout(self.HBoxLayout_sourceLimit)

        self.horizontalSpacer_17 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceLine2.addItem(self.horizontalSpacer_17)

        self.HBoxLayout_sourceNPLC = QHBoxLayout()
        self.HBoxLayout_sourceNPLC.setObjectName("HBoxLayout_sourceNPLC")
        self.label_sourceNPLC = QLabel(self.SourceBox)
        self.label_sourceNPLC.setObjectName("label_sourceNPLC")
        sizePolicy1.setHeightForWidth(self.label_sourceNPLC.sizePolicy().hasHeightForWidth())
        self.label_sourceNPLC.setSizePolicy(sizePolicy1)
        self.label_sourceNPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceNPLC.addWidget(self.label_sourceNPLC)

        self.lineEdit_sourceNPLC = QLineEdit(self.SourceBox)
        self.lineEdit_sourceNPLC.setObjectName("lineEdit_sourceNPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_sourceNPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_sourceNPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_sourceNPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_sourceNPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_sourceNPLC.addWidget(self.lineEdit_sourceNPLC)

        self.label_sourceNPLCUnits = QLabel(self.SourceBox)
        self.label_sourceNPLCUnits.setObjectName("label_sourceNPLCUnits")

        self.HBoxLayout_sourceNPLC.addWidget(self.label_sourceNPLCUnits)

        self.HBoxLayout_sourceLine2.addLayout(self.HBoxLayout_sourceNPLC)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceLine2.addItem(self.horizontalSpacer_19)

        self.HBoxLayout_sourceDelayMode = QHBoxLayout()
        self.HBoxLayout_sourceDelayMode.setObjectName("HBoxLayout_sourceDelayMode")
        self.label_sourceDelayMode = QLabel(self.SourceBox)
        self.label_sourceDelayMode.setObjectName("label_sourceDelayMode")
        sizePolicy1.setHeightForWidth(self.label_sourceDelayMode.sizePolicy().hasHeightForWidth())
        self.label_sourceDelayMode.setSizePolicy(sizePolicy1)
        self.label_sourceDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_sourceDelayMode.addWidget(self.label_sourceDelayMode)

        self.comboBox_sourceDelayMode = QComboBox(self.SourceBox)
        self.comboBox_sourceDelayMode.addItem("")
        self.comboBox_sourceDelayMode.addItem("")
        self.comboBox_sourceDelayMode.setObjectName("comboBox_sourceDelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_sourceDelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_sourceDelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_sourceDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_sourceDelayMode.addWidget(self.comboBox_sourceDelayMode)

        self.HBoxLayout_sourceLine2.addLayout(self.HBoxLayout_sourceDelayMode)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceLine2.addItem(self.horizontalSpacer_20)

        self.HBoxLayout_sourceDelay = QHBoxLayout()
        self.HBoxLayout_sourceDelay.setObjectName("HBoxLayout_sourceDelay")
        self.label_sourceDelay = QLabel(self.SourceBox)
        self.label_sourceDelay.setObjectName("label_sourceDelay")
        sizePolicy1.setHeightForWidth(self.label_sourceDelay.sizePolicy().hasHeightForWidth())
        self.label_sourceDelay.setSizePolicy(sizePolicy1)
        self.label_sourceDelay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceDelay.addWidget(self.label_sourceDelay)

        self.lineEdit_sourceDelay = QLineEdit(self.SourceBox)
        self.lineEdit_sourceDelay.setObjectName("lineEdit_sourceDelay")
        sizePolicy1.setHeightForWidth(self.lineEdit_sourceDelay.sizePolicy().hasHeightForWidth())
        self.lineEdit_sourceDelay.setSizePolicy(sizePolicy1)
        self.lineEdit_sourceDelay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_sourceDelay.addWidget(self.lineEdit_sourceDelay)

        self.label_sourceDelayUnits = QLabel(self.SourceBox)
        self.label_sourceDelayUnits.setObjectName("label_sourceDelayUnits")

        self.HBoxLayout_sourceDelay.addWidget(self.label_sourceDelayUnits)

        self.HBoxLayout_sourceLine2.addLayout(self.HBoxLayout_sourceDelay)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceLine2.addItem(self.horizontalSpacer_18)

        self.HBoxLayout_sourceLine2.setStretch(0, 10)
        self.HBoxLayout_sourceLine2.setStretch(1, 1)
        self.HBoxLayout_sourceLine2.setStretch(2, 10)
        self.HBoxLayout_sourceLine2.setStretch(3, 1)
        self.HBoxLayout_sourceLine2.setStretch(4, 10)
        self.HBoxLayout_sourceLine2.setStretch(5, 1)
        self.HBoxLayout_sourceLine2.setStretch(6, 10)
        self.HBoxLayout_sourceLine2.setStretch(7, 1)
        self.HBoxLayout_sourceLine2.setStretch(8, 10)
        self.HBoxLayout_sourceLine2.setStretch(9, 1)

        self.verticalLayout_6.addLayout(self.HBoxLayout_sourceLine2)

        self.HBoxLayout_singleChannel = QHBoxLayout()
        self.HBoxLayout_singleChannel.setObjectName("HBoxLayout_singleChannel")
        self.checkBox_singleChannel = QCheckBox(self.SourceBox)
        self.checkBox_singleChannel.setObjectName("checkBox_singleChannel")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_singleChannel)

        self.verticalLayout_6.addLayout(self.HBoxLayout_singleChannel)

        self.verticalLayout_5.addWidget(self.SourceBox)

        self.DrainBox = QGroupBox(self.groupBox_SMUGeneral)
        self.DrainBox.setObjectName("DrainBox")
        self.verticalLayout_7 = QVBoxLayout(self.DrainBox)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.HBoxLayout_generalDrain = QHBoxLayout()
        self.HBoxLayout_generalDrain.setObjectName("HBoxLayout_generalDrain")
        self.HBoxLayout_drainInject = QHBoxLayout()
        self.HBoxLayout_drainInject.setObjectName("HBoxLayout_drainInject")
        self.label_drainInject = QLabel(self.DrainBox)
        self.label_drainInject.setObjectName("label_drainInject")
        sizePolicy1.setHeightForWidth(self.label_drainInject.sizePolicy().hasHeightForWidth())
        self.label_drainInject.setSizePolicy(sizePolicy1)
        self.label_drainInject.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_drainInject.addWidget(self.label_drainInject)

        self.comboBox_drainInject = QComboBox(self.DrainBox)
        self.comboBox_drainInject.addItem("")
        self.comboBox_drainInject.addItem("")
        self.comboBox_drainInject.setObjectName("comboBox_drainInject")
        sizePolicy1.setHeightForWidth(self.comboBox_drainInject.sizePolicy().hasHeightForWidth())
        self.comboBox_drainInject.setSizePolicy(sizePolicy1)
        self.comboBox_drainInject.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainInject.addWidget(self.comboBox_drainInject)

        self.HBoxLayout_generalDrain.addLayout(self.HBoxLayout_drainInject)

        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_generalDrain.addItem(self.horizontalSpacer_23)

        self.HBoxLayout_drainSenseMode = QHBoxLayout()
        self.HBoxLayout_drainSenseMode.setObjectName("HBoxLayout_drainSenseMode")
        self.label_drainSenseMode = QLabel(self.DrainBox)
        self.label_drainSenseMode.setObjectName("label_drainSenseMode")
        sizePolicy1.setHeightForWidth(self.label_drainSenseMode.sizePolicy().hasHeightForWidth())
        self.label_drainSenseMode.setSizePolicy(sizePolicy1)
        self.label_drainSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainSenseMode.addWidget(self.label_drainSenseMode)

        self.comboBox_drainSenseMode = QComboBox(self.DrainBox)
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.setObjectName("comboBox_drainSenseMode")
        sizePolicy1.setHeightForWidth(self.comboBox_drainSenseMode.sizePolicy().hasHeightForWidth())
        self.comboBox_drainSenseMode.setSizePolicy(sizePolicy1)
        self.comboBox_drainSenseMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainSenseMode.addWidget(self.comboBox_drainSenseMode)

        self.HBoxLayout_generalDrain.addLayout(self.HBoxLayout_drainSenseMode)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_generalDrain.addItem(self.horizontalSpacer_24)

        self.HBoxLayout_generalDrain.setStretch(0, 10)
        self.HBoxLayout_generalDrain.setStretch(1, 1)
        self.HBoxLayout_generalDrain.setStretch(3, 20)

        self.verticalLayout_7.addLayout(self.HBoxLayout_generalDrain)

        self.HBoxLayout_drainLine2 = QHBoxLayout()
        self.HBoxLayout_drainLine2.setObjectName("HBoxLayout_drainLine2")
        self.HBoxLayout_drainStart = QHBoxLayout()
        self.HBoxLayout_drainStart.setObjectName("HBoxLayout_drainStart")
        self.label_drainSetValue = QLabel(self.DrainBox)
        self.label_drainSetValue.setObjectName("label_drainSetValue")
        sizePolicy1.setHeightForWidth(self.label_drainSetValue.sizePolicy().hasHeightForWidth())
        self.label_drainSetValue.setSizePolicy(sizePolicy1)
        self.label_drainSetValue.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainStart.addWidget(self.label_drainSetValue)

        self.lineEdit_drainSetValue = QLineEdit(self.DrainBox)
        self.lineEdit_drainSetValue.setObjectName("lineEdit_drainSetValue")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainSetValue.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainSetValue.setSizePolicy(sizePolicy1)
        self.lineEdit_drainSetValue.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainStart.addWidget(self.lineEdit_drainSetValue)

        self.label_drainSetValueUnits = QLabel(self.DrainBox)
        self.label_drainSetValueUnits.setObjectName("label_drainSetValueUnits")

        self.HBoxLayout_drainStart.addWidget(self.label_drainSetValueUnits)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainStart)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_22)

        self.HBoxLayout_drainLimit = QHBoxLayout()
        self.HBoxLayout_drainLimit.setObjectName("HBoxLayout_drainLimit")
        self.label_drainLimit = QLabel(self.DrainBox)
        self.label_drainLimit.setObjectName("label_drainLimit")
        sizePolicy1.setHeightForWidth(self.label_drainLimit.sizePolicy().hasHeightForWidth())
        self.label_drainLimit.setSizePolicy(sizePolicy1)
        self.label_drainLimit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainLimit.addWidget(self.label_drainLimit)

        self.lineEdit_drainLimit = QLineEdit(self.DrainBox)
        self.lineEdit_drainLimit.setObjectName("lineEdit_drainLimit")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainLimit.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainLimit.setSizePolicy(sizePolicy1)
        self.lineEdit_drainLimit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainLimit.addWidget(self.lineEdit_drainLimit)

        self.label_drainLimitUnits = QLabel(self.DrainBox)
        self.label_drainLimitUnits.setObjectName("label_drainLimitUnits")

        self.HBoxLayout_drainLimit.addWidget(self.label_drainLimitUnits)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainLimit)

        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_25)

        self.HBoxLayout_drainNPLC = QHBoxLayout()
        self.HBoxLayout_drainNPLC.setObjectName("HBoxLayout_drainNPLC")
        self.label_drainNPLC = QLabel(self.DrainBox)
        self.label_drainNPLC.setObjectName("label_drainNPLC")
        sizePolicy1.setHeightForWidth(self.label_drainNPLC.sizePolicy().hasHeightForWidth())
        self.label_drainNPLC.setSizePolicy(sizePolicy1)
        self.label_drainNPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainNPLC.addWidget(self.label_drainNPLC)

        self.lineEdit_drainNPLC = QLineEdit(self.DrainBox)
        self.lineEdit_drainNPLC.setObjectName("lineEdit_drainNPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainNPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainNPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_drainNPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_drainNPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_drainNPLC.addWidget(self.lineEdit_drainNPLC)

        self.label_drainNPLCUnits = QLabel(self.DrainBox)
        self.label_drainNPLCUnits.setObjectName("label_drainNPLCUnits")

        self.HBoxLayout_drainNPLC.addWidget(self.label_drainNPLCUnits)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainNPLC)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_26)

        self.HBoxLayout_drainDelayMode = QHBoxLayout()
        self.HBoxLayout_drainDelayMode.setObjectName("HBoxLayout_drainDelayMode")
        self.label_drainDelayMode = QLabel(self.DrainBox)
        self.label_drainDelayMode.setObjectName("label_drainDelayMode")
        sizePolicy1.setHeightForWidth(self.label_drainDelayMode.sizePolicy().hasHeightForWidth())
        self.label_drainDelayMode.setSizePolicy(sizePolicy1)
        self.label_drainDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainDelayMode.addWidget(self.label_drainDelayMode)

        self.comboBox_drainDelayMode = QComboBox(self.DrainBox)
        self.comboBox_drainDelayMode.addItem("")
        self.comboBox_drainDelayMode.addItem("")
        self.comboBox_drainDelayMode.setObjectName("comboBox_drainDelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_drainDelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_drainDelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_drainDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainDelayMode.addWidget(self.comboBox_drainDelayMode)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainDelayMode)

        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_27)

        self.HBoxLayout_drainDelay = QHBoxLayout()
        self.HBoxLayout_drainDelay.setObjectName("HBoxLayout_drainDelay")
        self.label_drainDelay = QLabel(self.DrainBox)
        self.label_drainDelay.setObjectName("label_drainDelay")
        sizePolicy1.setHeightForWidth(self.label_drainDelay.sizePolicy().hasHeightForWidth())
        self.label_drainDelay.setSizePolicy(sizePolicy1)
        self.label_drainDelay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainDelay.addWidget(self.label_drainDelay)

        self.lineEdit_drainDelay = QLineEdit(self.DrainBox)
        self.lineEdit_drainDelay.setObjectName("lineEdit_drainDelay")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainDelay.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainDelay.setSizePolicy(sizePolicy1)
        self.lineEdit_drainDelay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainDelay.addWidget(self.lineEdit_drainDelay)

        self.label_drainDelayUnits = QLabel(self.DrainBox)
        self.label_drainDelayUnits.setObjectName("label_drainDelayUnits")

        self.HBoxLayout_drainDelay.addWidget(self.label_drainDelayUnits)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainDelay)

        self.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_28)

        self.HBoxLayout_drainLine2.setStretch(0, 10)
        self.HBoxLayout_drainLine2.setStretch(1, 1)
        self.HBoxLayout_drainLine2.setStretch(2, 10)
        self.HBoxLayout_drainLine2.setStretch(3, 1)
        self.HBoxLayout_drainLine2.setStretch(4, 10)
        self.HBoxLayout_drainLine2.setStretch(5, 1)
        self.HBoxLayout_drainLine2.setStretch(6, 10)
        self.HBoxLayout_drainLine2.setStretch(7, 1)
        self.HBoxLayout_drainLine2.setStretch(8, 10)
        self.HBoxLayout_drainLine2.setStretch(9, 1)

        self.verticalLayout_7.addLayout(self.HBoxLayout_drainLine2)

        self.verticalLayout_5.addWidget(self.DrainBox)

        self.verticalLayout.addWidget(self.groupBox_SMUGeneral)

        self.fileBox = QGroupBox(self.groupBox_general)
        self.fileBox.setObjectName("fileBox")
        self.verticalLayout_2 = QVBoxLayout(self.fileBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pathLabel = QLabel(self.fileBox)
        self.pathLabel.setObjectName("pathLabel")
        self.pathLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.pathLabel)

        self.lineEdit_path = QLineEdit(self.fileBox)
        self.lineEdit_path.setObjectName("lineEdit_path")

        self.horizontalLayout_4.addWidget(self.lineEdit_path)

        self.directoryButton = QPushButton(self.fileBox)
        self.directoryButton.setObjectName("directoryButton")

        self.horizontalLayout_4.addWidget(self.directoryButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.filenameLabel = QLabel(self.fileBox)
        self.filenameLabel.setObjectName("filenameLabel")
        self.filenameLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_5.addWidget(self.filenameLabel)

        self.lineEdit_filename = QLineEdit(self.fileBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.horizontalLayout_5.addWidget(self.lineEdit_filename)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)

        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.sampleName_label = QLabel(self.fileBox)
        self.sampleName_label.setObjectName("sampleName_label")
        self.sampleName_label.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_6.addWidget(self.sampleName_label)

        self.lineEdit_sampleName = QLineEdit(self.fileBox)
        self.lineEdit_sampleName.setObjectName("lineEdit_sampleName")

        self.horizontalLayout_6.addWidget(self.lineEdit_sampleName)

        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_comment = QLabel(self.fileBox)
        self.label_comment.setObjectName("label_comment")
        self.label_comment.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_7.addWidget(self.label_comment)

        self.lineEdit_comment = QLineEdit(self.fileBox)
        self.lineEdit_comment.setObjectName("lineEdit_comment")
        self.lineEdit_comment.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_7.addWidget(self.lineEdit_comment)

        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.autosaveCheckBox = QCheckBox(self.fileBox)
        self.autosaveCheckBox.setObjectName("autosaveCheckBox")

        self.horizontalLayout.addWidget(self.autosaveCheckBox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.autosaveIntervalLable = QLabel(self.fileBox)
        self.autosaveIntervalLable.setObjectName("autosaveIntervalLable")

        self.horizontalLayout.addWidget(self.autosaveIntervalLable)

        self.autosaveLineEdit = QLineEdit(self.fileBox)
        self.autosaveLineEdit.setObjectName("autosaveLineEdit")
        self.autosaveLineEdit.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout.addWidget(self.autosaveLineEdit)

        self.autosaveintervalUnitslabel = QLabel(self.fileBox)
        self.autosaveintervalUnitslabel.setObjectName("autosaveintervalUnitslabel")

        self.horizontalLayout.addWidget(self.autosaveintervalUnitslabel)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout.addWidget(self.fileBox)

        self.verticalLayout_4.addWidget(self.groupBox_general)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.buttonBox = QGroupBox(self.scrollAreaWidgetContents)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3 = QVBoxLayout(self.buttonBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.runButton = QPushButton(self.buttonBox)
        self.runButton.setObjectName("runButton")
        self.runButton.setEnabled(False)
        self.runButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.runButton)

        self.stopButton = QPushButton(self.buttonBox)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setEnabled(False)
        self.stopButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.stopButton)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalLayout_4.addWidget(self.buttonBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 2)

        self.retranslateUi(Form)

        self.comboBox_channel.setCurrentIndex(-1)
        self.comboBox_inject.setCurrentIndex(0)
        self.comboBox_sourceSenseMode.setCurrentIndex(0)
        self.comboBox_sourceDelayMode.setCurrentIndex(0)
        self.comboBox_drainInject.setCurrentIndex(0)
        self.comboBox_drainSenseMode.setCurrentIndex(0)
        self.comboBox_drainDelayMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "timeIV", None))
        self.groupBox_general.setTitle("")
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.label.setText(QCoreApplication.translate("Form", "SMU Plugin", None))
        self.groupBox.setTitle("")
        self.stepLabel.setText(QCoreApplication.translate("Form", "Time step", None))
        self.stepUnitsLabel.setText(QCoreApplication.translate("Form", "s", None))
        self.stopTimerCheckBox.setText(QCoreApplication.translate("Form", "timer to stop", None))
        self.stopAfterlabel.setText(QCoreApplication.translate("Form", "Stop after", None))
        self.stopAfteUnitslabel.setText(QCoreApplication.translate("Form", "min", None))
        self.groupBox_SMUGeneral.setTitle(QCoreApplication.translate("Form", "SMU control", None))
        self.SourceBox.setTitle(QCoreApplication.translate("Form", "Source", None))
        self.label_Channel.setText(QCoreApplication.translate("Form", "Source channel", None))
        self.label_inject.setText(QCoreApplication.translate("Form", "Inject", None))
        self.comboBox_inject.setItemText(0, QCoreApplication.translate("Form", "current", None))
        self.comboBox_inject.setItemText(1, QCoreApplication.translate("Form", "voltage", None))

        self.label_sourceSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_sourceSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_sourceSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_sourceSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.label_sourceSetValue.setText(QCoreApplication.translate("Form", "I", None))
        self.lineEdit_sourceSetValue.setText(QCoreApplication.translate("Form", "0", None))
        self.label_sourceSetValueUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_sourceLimit.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_sourceLimit.setText(QCoreApplication.translate("Form", "0.05", None))
        self.label_sourceLimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_sourceNPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_sourceNPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_sourceNPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_sourceDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_sourceDelayMode.setItemText(0, QCoreApplication.translate("Form", "auto", None))
        self.comboBox_sourceDelayMode.setItemText(1, QCoreApplication.translate("Form", "manual", None))

        self.label_sourceDelay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_sourceDelay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_sourceDelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.checkBox_singleChannel.setText(QCoreApplication.translate("Form", "Use single channel", None))
        self.DrainBox.setTitle(QCoreApplication.translate("Form", "Drain", None))
        self.label_drainInject.setText(QCoreApplication.translate("Form", "Inject", None))
        self.comboBox_drainInject.setItemText(0, QCoreApplication.translate("Form", "current", None))
        self.comboBox_drainInject.setItemText(1, QCoreApplication.translate("Form", "voltage", None))

        self.label_drainSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_drainSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_drainSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_drainSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.label_drainSetValue.setText(QCoreApplication.translate("Form", "I", None))
        self.lineEdit_drainSetValue.setText(QCoreApplication.translate("Form", "0", None))
        self.label_drainSetValueUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_drainLimit.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_drainLimit.setText(QCoreApplication.translate("Form", "0.05", None))
        self.label_drainLimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_drainNPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_drainNPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_drainNPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_drainDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_drainDelayMode.setItemText(0, QCoreApplication.translate("Form", "auto", None))
        self.comboBox_drainDelayMode.setItemText(1, QCoreApplication.translate("Form", "manual", None))

        self.label_drainDelay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_drainDelay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_drainDelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.fileBox.setTitle("")
        self.pathLabel.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.filenameLabel.setText(QCoreApplication.translate("Form", "Filename", None))
        self.sampleName_label.setText(QCoreApplication.translate("Form", "Sample name", None))
        self.label_comment.setText(QCoreApplication.translate("Form", "Comment", None))
        self.autosaveCheckBox.setText(QCoreApplication.translate("Form", "use autosave", None))
        self.autosaveIntervalLable.setText(QCoreApplication.translate("Form", "Autosave interval", None))
        self.autosaveintervalUnitslabel.setText(QCoreApplication.translate("Form", "min", None))
        self.buttonBox.setTitle("")
        self.runButton.setText(QCoreApplication.translate("Form", "Run", None))
        self.stopButton.setText(QCoreApplication.translate("Form", "Stop", None))

    # retranslateUi
