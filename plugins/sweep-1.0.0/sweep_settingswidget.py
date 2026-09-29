################################################################################
## Form generated from reading UI file 'sweep_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1546, 1034)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1532, 1020))
        self.verticalLayout_10 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.groupBox_dep = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_dep.setObjectName("groupBox_dep")
        self.gridLayout_2 = QGridLayout(self.groupBox_dep)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.smuBox = QComboBox(self.groupBox_dep)
        self.smuBox.setObjectName("smuBox")

        self.gridLayout_2.addWidget(self.smuBox, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_dep)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.verticalLayout_10.addWidget(self.groupBox_dep)

        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.groupBox_general.setMinimumSize(QSize(0, 0))
        self.groupBox_general.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_general)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.HBoxLayout_general = QHBoxLayout()
        self.HBoxLayout_general.setObjectName("HBoxLayout_general")
        self.HBoxLayout_channel = QHBoxLayout()
        self.HBoxLayout_channel.setObjectName("HBoxLayout_channel")
        self.label_Channel = QLabel(self.groupBox_general)
        self.label_Channel.setObjectName("label_Channel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_Channel.sizePolicy().hasHeightForWidth())
        self.label_Channel.setSizePolicy(sizePolicy1)
        self.label_Channel.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_channel.addWidget(self.label_Channel)

        self.comboBox_channel = QComboBox(self.groupBox_general)
        self.comboBox_channel.setObjectName("comboBox_channel")
        sizePolicy1.setHeightForWidth(self.comboBox_channel.sizePolicy().hasHeightForWidth())
        self.comboBox_channel.setSizePolicy(sizePolicy1)
        self.comboBox_channel.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_channel.addWidget(self.comboBox_channel)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_channel)

        self.HBoxLayout_inject = QHBoxLayout()
        self.HBoxLayout_inject.setObjectName("HBoxLayout_inject")
        self.label_inject = QLabel(self.groupBox_general)
        self.label_inject.setObjectName("label_inject")
        sizePolicy1.setHeightForWidth(self.label_inject.sizePolicy().hasHeightForWidth())
        self.label_inject.setSizePolicy(sizePolicy1)
        self.label_inject.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_inject.addWidget(self.label_inject)

        self.comboBox_inject = QComboBox(self.groupBox_general)
        self.comboBox_inject.addItem("")
        self.comboBox_inject.addItem("")
        self.comboBox_inject.setObjectName("comboBox_inject")
        sizePolicy1.setHeightForWidth(self.comboBox_inject.sizePolicy().hasHeightForWidth())
        self.comboBox_inject.setSizePolicy(sizePolicy1)
        self.comboBox_inject.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_inject.addWidget(self.comboBox_inject)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_inject)

        self.HBoxLayout_repeat = QHBoxLayout()
        self.HBoxLayout_repeat.setObjectName("HBoxLayout_repeat")
        self.label_repeat = QLabel(self.groupBox_general)
        self.label_repeat.setObjectName("label_repeat")
        sizePolicy1.setHeightForWidth(self.label_repeat.sizePolicy().hasHeightForWidth())
        self.label_repeat.setSizePolicy(sizePolicy1)
        self.label_repeat.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_repeat.addWidget(self.label_repeat)

        self.lineEdit_repeat = QLineEdit(self.groupBox_general)
        self.lineEdit_repeat.setObjectName("lineEdit_repeat")
        sizePolicy1.setHeightForWidth(self.lineEdit_repeat.sizePolicy().hasHeightForWidth())
        self.lineEdit_repeat.setSizePolicy(sizePolicy1)
        self.lineEdit_repeat.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_repeat.addWidget(self.lineEdit_repeat)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_repeat)

        self.HBoxLayout_mode = QHBoxLayout()
        self.HBoxLayout_mode.setObjectName("HBoxLayout_mode")
        self.label_mode = QLabel(self.groupBox_general)
        self.label_mode.setObjectName("label_mode")
        sizePolicy1.setHeightForWidth(self.label_mode.sizePolicy().hasHeightForWidth())
        self.label_mode.setSizePolicy(sizePolicy1)
        self.label_mode.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_mode.addWidget(self.label_mode)

        self.comboBox_mode = QComboBox(self.groupBox_general)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName("comboBox_mode")
        sizePolicy1.setHeightForWidth(self.comboBox_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_mode.setSizePolicy(sizePolicy1)
        self.comboBox_mode.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_mode.addWidget(self.comboBox_mode)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_mode)

        self.HBoxLayout_sourceSenseMode = QHBoxLayout()
        self.HBoxLayout_sourceSenseMode.setObjectName("HBoxLayout_sourceSenseMode")
        self.label_sourceSenseMode = QLabel(self.groupBox_general)
        self.label_sourceSenseMode.setObjectName("label_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.label_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.label_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.label_sourceSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.label_sourceSenseMode)

        self.comboBox_sourceSenseMode = QComboBox(self.groupBox_general)
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
        self.HBoxLayout_general.setStretch(1, 10)
        self.HBoxLayout_general.setStretch(2, 10)
        self.HBoxLayout_general.setStretch(3, 10)
        self.HBoxLayout_general.setStretch(4, 10)
        self.HBoxLayout_general.setStretch(5, 10)

        self.verticalLayout_2.addLayout(self.HBoxLayout_general)

        self.HBoxLayout_singleChannel = QHBoxLayout()
        self.HBoxLayout_singleChannel.setObjectName("HBoxLayout_singleChannel")
        self.checkBox_singleChannel = QCheckBox(self.groupBox_general)
        self.checkBox_singleChannel.setObjectName("checkBox_singleChannel")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_singleChannel)

        self.checkBox_logSweep = QCheckBox(self.groupBox_general)
        self.checkBox_logSweep.setObjectName("checkBox_logSweep")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_logSweep)

        self.label_2 = QLabel(self.groupBox_general)
        self.label_2.setObjectName("label_2")

        self.HBoxLayout_singleChannel.addWidget(self.label_2)

        self.spinBox_asymp = QDoubleSpinBox(self.groupBox_general)
        self.spinBox_asymp.setObjectName("spinBox_asymp")
        self.spinBox_asymp.setMinimum(-99.000000000000000)

        self.HBoxLayout_singleChannel.addWidget(self.spinBox_asymp)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_singleChannel.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2.addLayout(self.HBoxLayout_singleChannel)

        self.verticalLayout_10.addWidget(self.groupBox_general)

        self.groupBox_sweep = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_sweep.setObjectName("groupBox_sweep")
        self.groupBox_sweep.setMinimumSize(QSize(0, 0))
        self.groupBox_sweep.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_sweep)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_continuousSweep = QGroupBox(self.groupBox_sweep)
        self.groupBox_continuousSweep.setObjectName("groupBox_continuousSweep")
        self.groupBox_continuousSweep.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_continuousSweep)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.HBoxLayout_continuousLine1 = QHBoxLayout()
        self.HBoxLayout_continuousLine1.setObjectName("HBoxLayout_continuousLine1")
        self.HBoxLayout_continuousStart = QHBoxLayout()
        self.HBoxLayout_continuousStart.setObjectName("HBoxLayout_continuousStart")
        self.label_continuousStart = QLabel(self.groupBox_continuousSweep)
        self.label_continuousStart.setObjectName("label_continuousStart")
        sizePolicy1.setHeightForWidth(self.label_continuousStart.sizePolicy().hasHeightForWidth())
        self.label_continuousStart.setSizePolicy(sizePolicy1)
        self.label_continuousStart.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_continuousStart.addWidget(self.label_continuousStart)

        self.lineEdit_continuousStart = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousStart.setObjectName("lineEdit_continuousStart")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousStart.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousStart.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousStart.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_continuousStart.addWidget(self.lineEdit_continuousStart)

        self.label_continuousStartUnits = QLabel(self.groupBox_continuousSweep)
        self.label_continuousStartUnits.setObjectName("label_continuousStartUnits")

        self.HBoxLayout_continuousStart.addWidget(self.label_continuousStartUnits)

        self.HBoxLayout_continuousLine1.addLayout(self.HBoxLayout_continuousStart)

        self.HBoxLayout_continuousEnd = QHBoxLayout()
        self.HBoxLayout_continuousEnd.setObjectName("HBoxLayout_continuousEnd")
        self.label_continuousEnd = QLabel(self.groupBox_continuousSweep)
        self.label_continuousEnd.setObjectName("label_continuousEnd")
        sizePolicy1.setHeightForWidth(self.label_continuousEnd.sizePolicy().hasHeightForWidth())
        self.label_continuousEnd.setSizePolicy(sizePolicy1)
        self.label_continuousEnd.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_continuousEnd.addWidget(self.label_continuousEnd)

        self.lineEdit_continuousEnd = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousEnd.setObjectName("lineEdit_continuousEnd")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousEnd.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousEnd.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousEnd.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_continuousEnd.addWidget(self.lineEdit_continuousEnd)

        self.label_continuousEndUnits = QLabel(self.groupBox_continuousSweep)
        self.label_continuousEndUnits.setObjectName("label_continuousEndUnits")

        self.HBoxLayout_continuousEnd.addWidget(self.label_continuousEndUnits)

        self.HBoxLayout_continuousLine1.addLayout(self.HBoxLayout_continuousEnd)

        self.HBoxLayout_continuousPoints = QHBoxLayout()
        self.HBoxLayout_continuousPoints.setObjectName("HBoxLayout_continuousPoints")
        self.label_continuousPoints = QLabel(self.groupBox_continuousSweep)
        self.label_continuousPoints.setObjectName("label_continuousPoints")
        sizePolicy1.setHeightForWidth(self.label_continuousPoints.sizePolicy().hasHeightForWidth())
        self.label_continuousPoints.setSizePolicy(sizePolicy1)
        self.label_continuousPoints.setMinimumSize(QSize(50, 0))

        self.HBoxLayout_continuousPoints.addWidget(self.label_continuousPoints)

        self.lineEdit_continuousPoints = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousPoints.setObjectName("lineEdit_continuousPoints")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousPoints.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousPoints.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousPoints.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_continuousPoints.addWidget(self.lineEdit_continuousPoints)

        self.HBoxLayout_continuousLine1.addLayout(self.HBoxLayout_continuousPoints)

        self.HBoxLayout_continuousLimit = QHBoxLayout()
        self.HBoxLayout_continuousLimit.setObjectName("HBoxLayout_continuousLimit")
        self.label_continuousLimit = QLabel(self.groupBox_continuousSweep)
        self.label_continuousLimit.setObjectName("label_continuousLimit")
        sizePolicy1.setHeightForWidth(self.label_continuousLimit.sizePolicy().hasHeightForWidth())
        self.label_continuousLimit.setSizePolicy(sizePolicy1)
        self.label_continuousLimit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_continuousLimit.addWidget(self.label_continuousLimit)

        self.lineEdit_continuousLimit = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousLimit.setObjectName("lineEdit_continuousLimit")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousLimit.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousLimit.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousLimit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_continuousLimit.addWidget(self.lineEdit_continuousLimit)

        self.label_continuousLimitUnits = QLabel(self.groupBox_continuousSweep)
        self.label_continuousLimitUnits.setObjectName("label_continuousLimitUnits")

        self.HBoxLayout_continuousLimit.addWidget(self.label_continuousLimitUnits)

        self.HBoxLayout_continuousLine1.addLayout(self.HBoxLayout_continuousLimit)

        self.HBoxLayout_continuousNPLC = QHBoxLayout()
        self.HBoxLayout_continuousNPLC.setObjectName("HBoxLayout_continuousNPLC")
        self.label_continuousNPLC = QLabel(self.groupBox_continuousSweep)
        self.label_continuousNPLC.setObjectName("label_continuousNPLC")
        sizePolicy1.setHeightForWidth(self.label_continuousNPLC.sizePolicy().hasHeightForWidth())
        self.label_continuousNPLC.setSizePolicy(sizePolicy1)
        self.label_continuousNPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_continuousNPLC.addWidget(self.label_continuousNPLC)

        self.lineEdit_continuousNPLC = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousNPLC.setObjectName("lineEdit_continuousNPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousNPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousNPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousNPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_continuousNPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_continuousNPLC.addWidget(self.lineEdit_continuousNPLC)

        self.label_continuousNPLCUnits = QLabel(self.groupBox_continuousSweep)
        self.label_continuousNPLCUnits.setObjectName("label_continuousNPLCUnits")

        self.HBoxLayout_continuousNPLC.addWidget(self.label_continuousNPLCUnits)

        self.HBoxLayout_continuousLine1.addLayout(self.HBoxLayout_continuousNPLC)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_continuousLine1.addItem(self.horizontalSpacer_7)

        self.HBoxLayout_continuousLine1.setStretch(0, 10)
        self.HBoxLayout_continuousLine1.setStretch(1, 10)
        self.HBoxLayout_continuousLine1.setStretch(2, 10)
        self.HBoxLayout_continuousLine1.setStretch(3, 10)
        self.HBoxLayout_continuousLine1.setStretch(4, 10)
        self.HBoxLayout_continuousLine1.setStretch(5, 13)

        self.verticalLayout_3.addLayout(self.HBoxLayout_continuousLine1)

        self.HBoxLayout_continuousLine2 = QHBoxLayout()
        self.HBoxLayout_continuousLine2.setObjectName("HBoxLayout_continuousLine2")
        self.HBoxLayout_continuousDelayMode = QHBoxLayout()
        self.HBoxLayout_continuousDelayMode.setObjectName("HBoxLayout_continuousDelayMode")
        self.label_continuousDelayMode = QLabel(self.groupBox_continuousSweep)
        self.label_continuousDelayMode.setObjectName("label_continuousDelayMode")
        sizePolicy1.setHeightForWidth(self.label_continuousDelayMode.sizePolicy().hasHeightForWidth())
        self.label_continuousDelayMode.setSizePolicy(sizePolicy1)
        self.label_continuousDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_continuousDelayMode.addWidget(self.label_continuousDelayMode)

        self.comboBox_continuousDelayMode = QComboBox(self.groupBox_continuousSweep)
        self.comboBox_continuousDelayMode.addItem("")
        self.comboBox_continuousDelayMode.addItem("")
        self.comboBox_continuousDelayMode.setObjectName("comboBox_continuousDelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_continuousDelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_continuousDelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_continuousDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_continuousDelayMode.addWidget(self.comboBox_continuousDelayMode)

        self.HBoxLayout_continuousLine2.addLayout(self.HBoxLayout_continuousDelayMode)

        self.HBoxLayout_continuousDelay = QHBoxLayout()
        self.HBoxLayout_continuousDelay.setObjectName("HBoxLayout_continuousDelay")
        self.label_continuousDelay = QLabel(self.groupBox_continuousSweep)
        self.label_continuousDelay.setObjectName("label_continuousDelay")
        sizePolicy1.setHeightForWidth(self.label_continuousDelay.sizePolicy().hasHeightForWidth())
        self.label_continuousDelay.setSizePolicy(sizePolicy1)
        self.label_continuousDelay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_continuousDelay.addWidget(self.label_continuousDelay)

        self.lineEdit_continuousDelay = QLineEdit(self.groupBox_continuousSweep)
        self.lineEdit_continuousDelay.setObjectName("lineEdit_continuousDelay")
        sizePolicy1.setHeightForWidth(self.lineEdit_continuousDelay.sizePolicy().hasHeightForWidth())
        self.lineEdit_continuousDelay.setSizePolicy(sizePolicy1)
        self.lineEdit_continuousDelay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_continuousDelay.addWidget(self.lineEdit_continuousDelay)

        self.label_continuousDelayUnits = QLabel(self.groupBox_continuousSweep)
        self.label_continuousDelayUnits.setObjectName("label_continuousDelayUnits")

        self.HBoxLayout_continuousDelay.addWidget(self.label_continuousDelayUnits)

        self.HBoxLayout_continuousLine2.addLayout(self.HBoxLayout_continuousDelay)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_continuousLine2.addItem(self.horizontalSpacer_13)

        self.HBoxLayout_continuousLine2.setStretch(0, 10)
        self.HBoxLayout_continuousLine2.setStretch(1, 10)
        self.HBoxLayout_continuousLine2.setStretch(2, 43)

        self.verticalLayout_3.addLayout(self.HBoxLayout_continuousLine2)

        self.verticalLayout_4.addWidget(self.groupBox_continuousSweep)

        self.groupBox_pulsedSweep = QGroupBox(self.groupBox_sweep)
        self.groupBox_pulsedSweep.setObjectName("groupBox_pulsedSweep")
        self.groupBox_pulsedSweep.setEnabled(True)
        self.groupBox_pulsedSweep.setMinimumSize(QSize(0, 0))
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_pulsedSweep)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.HBoxLayout_pulsedLine2 = QHBoxLayout()
        self.HBoxLayout_pulsedLine2.setObjectName("HBoxLayout_pulsedLine2")
        self.HBoxLayout_pulsedDelayMode = QHBoxLayout()
        self.HBoxLayout_pulsedDelayMode.setObjectName("HBoxLayout_pulsedDelayMode")
        self.label_pulsedDelayMode = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedDelayMode.setObjectName("label_pulsedDelayMode")
        sizePolicy1.setHeightForWidth(self.label_pulsedDelayMode.sizePolicy().hasHeightForWidth())
        self.label_pulsedDelayMode.setSizePolicy(sizePolicy1)
        self.label_pulsedDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.label_pulsedDelayMode)

        self.comboBox_pulsedDelayMode = QComboBox(self.groupBox_pulsedSweep)
        self.comboBox_pulsedDelayMode.addItem("")
        self.comboBox_pulsedDelayMode.addItem("")
        self.comboBox_pulsedDelayMode.setObjectName("comboBox_pulsedDelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_pulsedDelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_pulsedDelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_pulsedDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.comboBox_pulsedDelayMode)

        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelayMode)

        self.HBoxLayout_pulsedDelay = QHBoxLayout()
        self.HBoxLayout_pulsedDelay.setObjectName("HBoxLayout_pulsedDelay")
        self.label_pulsedDelay = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedDelay.setObjectName("label_pulsedDelay")
        sizePolicy1.setHeightForWidth(self.label_pulsedDelay.sizePolicy().hasHeightForWidth())
        self.label_pulsedDelay.setSizePolicy(sizePolicy1)
        self.label_pulsedDelay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.label_pulsedDelay)

        self.lineEdit_pulsedDelay = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedDelay.setObjectName("lineEdit_pulsedDelay")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedDelay.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedDelay.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedDelay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.lineEdit_pulsedDelay)

        self.label_pulsedDelayUnits = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedDelayUnits.setObjectName("label_pulsedDelayUnits")

        self.HBoxLayout_pulsedDelay.addWidget(self.label_pulsedDelayUnits)

        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelay)

        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_pulsedLine2.addItem(self.horizontalSpacer_18)

        self.HBoxLayout_pulsedLine2.setStretch(0, 10)
        self.HBoxLayout_pulsedLine2.setStretch(1, 10)
        self.HBoxLayout_pulsedLine2.setStretch(2, 43)

        self.verticalLayout_9.addLayout(self.HBoxLayout_pulsedLine2)

        self.HBoxLayout_pulsedLine1 = QHBoxLayout()
        self.HBoxLayout_pulsedLine1.setObjectName("HBoxLayout_pulsedLine1")
        self.HBoxLayout_pulsedStart = QHBoxLayout()
        self.HBoxLayout_pulsedStart.setObjectName("HBoxLayout_pulsedStart")
        self.label_continuousStart_2 = QLabel(self.groupBox_pulsedSweep)
        self.label_continuousStart_2.setObjectName("label_continuousStart_2")
        sizePolicy1.setHeightForWidth(self.label_continuousStart_2.sizePolicy().hasHeightForWidth())
        self.label_continuousStart_2.setSizePolicy(sizePolicy1)
        self.label_continuousStart_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.label_continuousStart_2)

        self.lineEdit_pulsedStart = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedStart.setObjectName("lineEdit_pulsedStart")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedStart.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedStart.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedStart.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.lineEdit_pulsedStart)

        self.label_pulsedStartUnits = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedStartUnits.setObjectName("label_pulsedStartUnits")

        self.HBoxLayout_pulsedStart.addWidget(self.label_pulsedStartUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedStart)

        self.HBoxLayout_pulsedEnd = QHBoxLayout()
        self.HBoxLayout_pulsedEnd.setObjectName("HBoxLayout_pulsedEnd")
        self.label_continuousEnd_2 = QLabel(self.groupBox_pulsedSweep)
        self.label_continuousEnd_2.setObjectName("label_continuousEnd_2")
        sizePolicy1.setHeightForWidth(self.label_continuousEnd_2.sizePolicy().hasHeightForWidth())
        self.label_continuousEnd_2.setSizePolicy(sizePolicy1)
        self.label_continuousEnd_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.label_continuousEnd_2)

        self.lineEdit_pulsedEnd = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedEnd.setObjectName("lineEdit_pulsedEnd")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedEnd.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedEnd.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedEnd.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.lineEdit_pulsedEnd)

        self.label_pulsedEndUnits = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedEndUnits.setObjectName("label_pulsedEndUnits")

        self.HBoxLayout_pulsedEnd.addWidget(self.label_pulsedEndUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedEnd)

        self.HBoxLayout_pulsedPoints = QHBoxLayout()
        self.HBoxLayout_pulsedPoints.setObjectName("HBoxLayout_pulsedPoints")
        self.label_pulsedPoints = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedPoints.setObjectName("label_pulsedPoints")
        sizePolicy1.setHeightForWidth(self.label_pulsedPoints.sizePolicy().hasHeightForWidth())
        self.label_pulsedPoints.setSizePolicy(sizePolicy1)
        self.label_pulsedPoints.setMinimumSize(QSize(50, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.label_pulsedPoints)

        self.lineEdit_pulsedPoints = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedPoints.setObjectName("lineEdit_pulsedPoints")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedPoints.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedPoints.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedPoints.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.lineEdit_pulsedPoints)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPoints)

        self.HBoxLayout_pulsedLimit = QHBoxLayout()
        self.HBoxLayout_pulsedLimit.setObjectName("HBoxLayout_pulsedLimit")
        self.label_continuousLimit_2 = QLabel(self.groupBox_pulsedSweep)
        self.label_continuousLimit_2.setObjectName("label_continuousLimit_2")
        sizePolicy1.setHeightForWidth(self.label_continuousLimit_2.sizePolicy().hasHeightForWidth())
        self.label_continuousLimit_2.setSizePolicy(sizePolicy1)
        self.label_continuousLimit_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.label_continuousLimit_2)

        self.lineEdit_pulsedLimit = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedLimit.setObjectName("lineEdit_pulsedLimit")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedLimit.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedLimit.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedLimit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.lineEdit_pulsedLimit)

        self.label_pulsedLimitUnits = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedLimitUnits.setObjectName("label_pulsedLimitUnits")

        self.HBoxLayout_pulsedLimit.addWidget(self.label_pulsedLimitUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedLimit)

        self.HBoxLayout_pulsedNPLC = QHBoxLayout()
        self.HBoxLayout_pulsedNPLC.setObjectName("HBoxLayout_pulsedNPLC")
        self.label_pulsedNPLC = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedNPLC.setObjectName("label_pulsedNPLC")
        sizePolicy1.setHeightForWidth(self.label_pulsedNPLC.sizePolicy().hasHeightForWidth())
        self.label_pulsedNPLC.setSizePolicy(sizePolicy1)
        self.label_pulsedNPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_pulsedNPLC)

        self.lineEdit_pulsedNPLC = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedNPLC.setObjectName("lineEdit_pulsedNPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedNPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedNPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedNPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_pulsedNPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.lineEdit_pulsedNPLC)

        self.label_pulsedNPLCUnits = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedNPLCUnits.setObjectName("label_pulsedNPLCUnits")

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_pulsedNPLCUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedNPLC)

        self.HBoxLayout_pulsedPause = QHBoxLayout()
        self.HBoxLayout_pulsedPause.setObjectName("HBoxLayout_pulsedPause")
        self.label_pulsedPause_2 = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedPause_2.setObjectName("label_pulsedPause_2")
        sizePolicy1.setHeightForWidth(self.label_pulsedPause_2.sizePolicy().hasHeightForWidth())
        self.label_pulsedPause_2.setSizePolicy(sizePolicy1)
        self.label_pulsedPause_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause_2)

        self.lineEdit_pulsedPause = QLineEdit(self.groupBox_pulsedSweep)
        self.lineEdit_pulsedPause.setObjectName("lineEdit_pulsedPause")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulsedPause.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulsedPause.setSizePolicy(sizePolicy1)
        self.lineEdit_pulsedPause.setMinimumSize(QSize(20, 0))
        self.lineEdit_pulsedPause.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.lineEdit_pulsedPause)

        self.label_pulsedPause = QLabel(self.groupBox_pulsedSweep)
        self.label_pulsedPause.setObjectName("label_pulsedPause")

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPause)

        self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_pulsedLine1.addItem(self.horizontalSpacer_25)

        self.HBoxLayout_pulsedLine1.setStretch(0, 10)
        self.HBoxLayout_pulsedLine1.setStretch(1, 10)
        self.HBoxLayout_pulsedLine1.setStretch(2, 10)
        self.HBoxLayout_pulsedLine1.setStretch(3, 10)
        self.HBoxLayout_pulsedLine1.setStretch(4, 10)
        self.HBoxLayout_pulsedLine1.setStretch(5, 10)
        self.HBoxLayout_pulsedLine1.setStretch(6, 1)

        self.verticalLayout_9.addLayout(self.HBoxLayout_pulsedLine1)

        self.verticalLayout_4.addWidget(self.groupBox_pulsedSweep)

        self.groupBox_drainSweep = QGroupBox(self.groupBox_sweep)
        self.groupBox_drainSweep.setObjectName("groupBox_drainSweep")
        self.groupBox_drainSweep.setMinimumSize(QSize(0, 0))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_drainSweep)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.HBoxLayout_drainLine1 = QHBoxLayout()
        self.HBoxLayout_drainLine1.setObjectName("HBoxLayout_drainLine1")
        self.HBoxLayout_drainStart = QHBoxLayout()
        self.HBoxLayout_drainStart.setObjectName("HBoxLayout_drainStart")
        self.label_drainStart = QLabel(self.groupBox_drainSweep)
        self.label_drainStart.setObjectName("label_drainStart")
        sizePolicy1.setHeightForWidth(self.label_drainStart.sizePolicy().hasHeightForWidth())
        self.label_drainStart.setSizePolicy(sizePolicy1)
        self.label_drainStart.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainStart.addWidget(self.label_drainStart)

        self.lineEdit_drainStart = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainStart.setObjectName("lineEdit_drainStart")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainStart.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainStart.setSizePolicy(sizePolicy1)
        self.lineEdit_drainStart.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainStart.addWidget(self.lineEdit_drainStart)

        self.label_drainStartUnits = QLabel(self.groupBox_drainSweep)
        self.label_drainStartUnits.setObjectName("label_drainStartUnits")

        self.HBoxLayout_drainStart.addWidget(self.label_drainStartUnits)

        self.HBoxLayout_drainLine1.addLayout(self.HBoxLayout_drainStart)

        self.HBoxLayout_drainEnd = QHBoxLayout()
        self.HBoxLayout_drainEnd.setObjectName("HBoxLayout_drainEnd")
        self.label_drainEnd = QLabel(self.groupBox_drainSweep)
        self.label_drainEnd.setObjectName("label_drainEnd")
        sizePolicy1.setHeightForWidth(self.label_drainEnd.sizePolicy().hasHeightForWidth())
        self.label_drainEnd.setSizePolicy(sizePolicy1)
        self.label_drainEnd.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainEnd.addWidget(self.label_drainEnd)

        self.lineEdit_drainEnd = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainEnd.setObjectName("lineEdit_drainEnd")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainEnd.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainEnd.setSizePolicy(sizePolicy1)
        self.lineEdit_drainEnd.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainEnd.addWidget(self.lineEdit_drainEnd)

        self.label_drainEndUnits = QLabel(self.groupBox_drainSweep)
        self.label_drainEndUnits.setObjectName("label_drainEndUnits")

        self.HBoxLayout_drainEnd.addWidget(self.label_drainEndUnits)

        self.HBoxLayout_drainLine1.addLayout(self.HBoxLayout_drainEnd)

        self.HBoxLayout_drainPoints = QHBoxLayout()
        self.HBoxLayout_drainPoints.setObjectName("HBoxLayout_drainPoints")
        self.label_drainPoints = QLabel(self.groupBox_drainSweep)
        self.label_drainPoints.setObjectName("label_drainPoints")
        sizePolicy1.setHeightForWidth(self.label_drainPoints.sizePolicy().hasHeightForWidth())
        self.label_drainPoints.setSizePolicy(sizePolicy1)
        self.label_drainPoints.setMinimumSize(QSize(50, 0))

        self.HBoxLayout_drainPoints.addWidget(self.label_drainPoints)

        self.lineEdit_drainPoints = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainPoints.setObjectName("lineEdit_drainPoints")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainPoints.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainPoints.setSizePolicy(sizePolicy1)
        self.lineEdit_drainPoints.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainPoints.addWidget(self.lineEdit_drainPoints)

        self.HBoxLayout_drainLine1.addLayout(self.HBoxLayout_drainPoints)

        self.HBoxLayout_drainLimit = QHBoxLayout()
        self.HBoxLayout_drainLimit.setObjectName("HBoxLayout_drainLimit")
        self.label_drainLimit = QLabel(self.groupBox_drainSweep)
        self.label_drainLimit.setObjectName("label_drainLimit")
        sizePolicy1.setHeightForWidth(self.label_drainLimit.sizePolicy().hasHeightForWidth())
        self.label_drainLimit.setSizePolicy(sizePolicy1)
        self.label_drainLimit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainLimit.addWidget(self.label_drainLimit)

        self.lineEdit_drainLimit = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainLimit.setObjectName("lineEdit_drainLimit")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainLimit.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainLimit.setSizePolicy(sizePolicy1)
        self.lineEdit_drainLimit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainLimit.addWidget(self.lineEdit_drainLimit)

        self.label_drainLimitUnits = QLabel(self.groupBox_drainSweep)
        self.label_drainLimitUnits.setObjectName("label_drainLimitUnits")

        self.HBoxLayout_drainLimit.addWidget(self.label_drainLimitUnits)

        self.HBoxLayout_drainLine1.addLayout(self.HBoxLayout_drainLimit)

        self.HBoxLayout_drainNPLC = QHBoxLayout()
        self.HBoxLayout_drainNPLC.setObjectName("HBoxLayout_drainNPLC")
        self.label_drainNPLC = QLabel(self.groupBox_drainSweep)
        self.label_drainNPLC.setObjectName("label_drainNPLC")
        sizePolicy1.setHeightForWidth(self.label_drainNPLC.sizePolicy().hasHeightForWidth())
        self.label_drainNPLC.setSizePolicy(sizePolicy1)
        self.label_drainNPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainNPLC.addWidget(self.label_drainNPLC)

        self.lineEdit_drainNPLC = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainNPLC.setObjectName("lineEdit_drainNPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainNPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainNPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_drainNPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_drainNPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_drainNPLC.addWidget(self.lineEdit_drainNPLC)

        self.label_drainNPLCUnits = QLabel(self.groupBox_drainSweep)
        self.label_drainNPLCUnits.setObjectName("label_drainNPLCUnits")

        self.HBoxLayout_drainNPLC.addWidget(self.label_drainNPLCUnits)

        self.HBoxLayout_drainLine1.addLayout(self.HBoxLayout_drainNPLC)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine1.addItem(self.horizontalSpacer_30)

        self.HBoxLayout_drainLine1.setStretch(0, 10)
        self.HBoxLayout_drainLine1.setStretch(1, 10)
        self.HBoxLayout_drainLine1.setStretch(2, 10)
        self.HBoxLayout_drainLine1.setStretch(3, 10)
        self.HBoxLayout_drainLine1.setStretch(4, 10)
        self.HBoxLayout_drainLine1.setStretch(5, 13)

        self.verticalLayout_5.addLayout(self.HBoxLayout_drainLine1)

        self.HBoxLayout_drainLine2 = QHBoxLayout()
        self.HBoxLayout_drainLine2.setObjectName("HBoxLayout_drainLine2")
        self.HBoxLayout_drainDelayMode = QHBoxLayout()
        self.HBoxLayout_drainDelayMode.setObjectName("HBoxLayout_drainDelayMode")
        self.label_drainDelayMode = QLabel(self.groupBox_drainSweep)
        self.label_drainDelayMode.setObjectName("label_drainDelayMode")
        sizePolicy1.setHeightForWidth(self.label_drainDelayMode.sizePolicy().hasHeightForWidth())
        self.label_drainDelayMode.setSizePolicy(sizePolicy1)
        self.label_drainDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainDelayMode.addWidget(self.label_drainDelayMode)

        self.comboBox_drainDelayMode = QComboBox(self.groupBox_drainSweep)
        self.comboBox_drainDelayMode.addItem("")
        self.comboBox_drainDelayMode.addItem("")
        self.comboBox_drainDelayMode.setObjectName("comboBox_drainDelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_drainDelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_drainDelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_drainDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainDelayMode.addWidget(self.comboBox_drainDelayMode)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainDelayMode)

        self.HBoxLayout_drainDelay = QHBoxLayout()
        self.HBoxLayout_drainDelay.setObjectName("HBoxLayout_drainDelay")
        self.label_drainDelay = QLabel(self.groupBox_drainSweep)
        self.label_drainDelay.setObjectName("label_drainDelay")
        sizePolicy1.setHeightForWidth(self.label_drainDelay.sizePolicy().hasHeightForWidth())
        self.label_drainDelay.setSizePolicy(sizePolicy1)
        self.label_drainDelay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainDelay.addWidget(self.label_drainDelay)

        self.lineEdit_drainDelay = QLineEdit(self.groupBox_drainSweep)
        self.lineEdit_drainDelay.setObjectName("lineEdit_drainDelay")
        sizePolicy1.setHeightForWidth(self.lineEdit_drainDelay.sizePolicy().hasHeightForWidth())
        self.lineEdit_drainDelay.setSizePolicy(sizePolicy1)
        self.lineEdit_drainDelay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_drainDelay.addWidget(self.lineEdit_drainDelay)

        self.label_drainDelayUnits = QLabel(self.groupBox_drainSweep)
        self.label_drainDelayUnits.setObjectName("label_drainDelayUnits")

        self.HBoxLayout_drainDelay.addWidget(self.label_drainDelayUnits)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainDelay)

        self.HBoxLayout_drainSenseMode = QHBoxLayout()
        self.HBoxLayout_drainSenseMode.setObjectName("HBoxLayout_drainSenseMode")
        self.label_drainSenseMode = QLabel(self.groupBox_drainSweep)
        self.label_drainSenseMode.setObjectName("label_drainSenseMode")
        sizePolicy1.setHeightForWidth(self.label_drainSenseMode.sizePolicy().hasHeightForWidth())
        self.label_drainSenseMode.setSizePolicy(sizePolicy1)
        self.label_drainSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_drainSenseMode.addWidget(self.label_drainSenseMode)

        self.comboBox_drainSenseMode = QComboBox(self.groupBox_drainSweep)
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.addItem("")
        self.comboBox_drainSenseMode.setObjectName("comboBox_drainSenseMode")
        sizePolicy1.setHeightForWidth(self.comboBox_drainSenseMode.sizePolicy().hasHeightForWidth())
        self.comboBox_drainSenseMode.setSizePolicy(sizePolicy1)
        self.comboBox_drainSenseMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_drainSenseMode.addWidget(self.comboBox_drainSenseMode)

        self.HBoxLayout_drainLine2.addLayout(self.HBoxLayout_drainSenseMode)

        self.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainLine2.addItem(self.horizontalSpacer_32)

        self.HBoxLayout_drainLine2.setStretch(0, 10)
        self.HBoxLayout_drainLine2.setStretch(1, 10)
        self.HBoxLayout_drainLine2.setStretch(2, 10)
        self.HBoxLayout_drainLine2.setStretch(3, 40)

        self.verticalLayout_5.addLayout(self.HBoxLayout_drainLine2)

        self.verticalLayout_4.addWidget(self.groupBox_drainSweep)

        self.verticalLayout_10.addWidget(self.groupBox_sweep)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_plotUpdate = QLabel(self.groupBox)
        self.label_plotUpdate.setObjectName("label_plotUpdate")
        self.label_plotUpdate.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_6.addWidget(self.label_plotUpdate)

        self.spinBox_plotUpdate = QSpinBox(self.groupBox)
        self.spinBox_plotUpdate.setObjectName("spinBox_plotUpdate")
        self.spinBox_plotUpdate.setMaximumSize(QSize(80, 16777215))
        self.spinBox_plotUpdate.setMinimum(1)
        self.spinBox_plotUpdate.setMaximum(20)

        self.horizontalLayout_6.addWidget(self.spinBox_plotUpdate)

        self.label_plotUpdateUnit = QLabel(self.groupBox)
        self.label_plotUpdateUnit.setObjectName("label_plotUpdateUnit")

        self.horizontalLayout_6.addWidget(self.label_plotUpdateUnit)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelPrescaler = QLabel(self.groupBox)
        self.labelPrescaler.setObjectName("labelPrescaler")
        self.labelPrescaler.setMinimumSize(QSize(200, 0))

        self.horizontalLayout.addWidget(self.labelPrescaler)

        self.prescalerEdit = QLineEdit(self.groupBox)
        self.prescalerEdit.setObjectName("prescalerEdit")
        self.prescalerEdit.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout.addWidget(self.prescalerEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout_10.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(66, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_2)

        self.fileBox = QGroupBox(self.scrollAreaWidgetContents)
        self.fileBox.setObjectName("fileBox")
        self.verticalLayout_6 = QVBoxLayout(self.fileBox)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
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

        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.filenameLabel = QLabel(self.fileBox)
        self.filenameLabel.setObjectName("filenameLabel")
        self.filenameLabel.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_5.addWidget(self.filenameLabel)

        self.lineEdit_filename = QLineEdit(self.fileBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.horizontalLayout_5.addWidget(self.lineEdit_filename)

        self.horizontalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_19)

        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.sampleName_label = QLabel(self.fileBox)
        self.sampleName_label.setObjectName("sampleName_label")
        self.sampleName_label.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_9.addWidget(self.sampleName_label)

        self.lineEdit_sampleName = QLineEdit(self.fileBox)
        self.lineEdit_sampleName.setObjectName("lineEdit_sampleName")

        self.horizontalLayout_9.addWidget(self.lineEdit_sampleName)

        self.verticalLayout_6.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_comment = QLabel(self.fileBox)
        self.label_comment.setObjectName("label_comment")
        self.label_comment.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_10.addWidget(self.label_comment)

        self.lineEdit_comment = QLineEdit(self.fileBox)
        self.lineEdit_comment.setObjectName("lineEdit_comment")
        self.lineEdit_comment.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_10.addWidget(self.lineEdit_comment)

        self.verticalLayout_6.addLayout(self.horizontalLayout_10)

        self.verticalLayout_10.addWidget(self.fileBox)

        self.buttonBox = QGroupBox(self.scrollAreaWidgetContents)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_8 = QVBoxLayout(self.buttonBox)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.runButton = QPushButton(self.buttonBox)
        self.runButton.setObjectName("runButton")
        self.runButton.setEnabled(True)
        self.runButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_12.addWidget(self.runButton)

        self.stopButton = QPushButton(self.buttonBox)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setEnabled(False)
        self.stopButton.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_12.addWidget(self.stopButton)

        self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_21)

        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.verticalLayout_10.addWidget(self.buttonBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        self.comboBox_channel.setCurrentIndex(-1)
        self.comboBox_inject.setCurrentIndex(0)
        self.comboBox_mode.setCurrentIndex(0)
        self.comboBox_sourceSenseMode.setCurrentIndex(0)
        self.comboBox_continuousDelayMode.setCurrentIndex(0)
        self.comboBox_pulsedDelayMode.setCurrentIndex(0)
        self.comboBox_drainDelayMode.setCurrentIndex(0)
        self.comboBox_drainSenseMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Sweep", None))
        self.groupBox_dep.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.label.setText(QCoreApplication.translate("Form", "SMU plugin", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "General", None))
        self.label_Channel.setText(QCoreApplication.translate("Form", "Source channel", None))
        self.label_inject.setText(QCoreApplication.translate("Form", "Inject", None))
        self.comboBox_inject.setItemText(0, QCoreApplication.translate("Form", "Current", None))
        self.comboBox_inject.setItemText(1, QCoreApplication.translate("Form", "Voltage", None))

        self.label_repeat.setText(QCoreApplication.translate("Form", "Repeat", None))
        self.lineEdit_repeat.setText(QCoreApplication.translate("Form", "1", None))
        self.label_mode.setText(QCoreApplication.translate("Form", "Mode", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("Form", "Continuous", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("Form", "Pulsed", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Form", "Mixed", None))

        self.label_sourceSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_sourceSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_sourceSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_sourceSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.checkBox_singleChannel.setText(QCoreApplication.translate("Form", "Use single channel", None))
        self.checkBox_logSweep.setText(QCoreApplication.translate("Form", "Logarithmic sweep", None))
        self.label_2.setText(QCoreApplication.translate("Form", "asymptote", None))
        self.groupBox_sweep.setTitle(QCoreApplication.translate("Form", "Sweep", None))
        self.groupBox_continuousSweep.setTitle(QCoreApplication.translate("Form", "Continuous", None))
        self.label_continuousStart.setText(QCoreApplication.translate("Form", "Start", None))
        self.lineEdit_continuousStart.setText(QCoreApplication.translate("Form", "0", None))
        self.label_continuousStartUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_continuousEnd.setText(QCoreApplication.translate("Form", "End", None))
        self.lineEdit_continuousEnd.setText(QCoreApplication.translate("Form", "0.1", None))
        self.label_continuousEndUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_continuousPoints.setText(QCoreApplication.translate("Form", "Points", None))
        self.lineEdit_continuousPoints.setText(QCoreApplication.translate("Form", "2", None))
        self.label_continuousLimit.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_continuousLimit.setText(QCoreApplication.translate("Form", "0.05", None))
        self.label_continuousLimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_continuousNPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_continuousNPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_continuousNPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_continuousDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_continuousDelayMode.setItemText(0, QCoreApplication.translate("Form", "Auto", None))
        self.comboBox_continuousDelayMode.setItemText(1, QCoreApplication.translate("Form", "Manual", None))

        self.label_continuousDelay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_continuousDelay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_continuousDelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.groupBox_pulsedSweep.setTitle(QCoreApplication.translate("Form", "Pulsed", None))
        self.label_pulsedDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_pulsedDelayMode.setItemText(0, QCoreApplication.translate("Form", "Auto", None))
        self.comboBox_pulsedDelayMode.setItemText(1, QCoreApplication.translate("Form", "Manual", None))

        self.label_pulsedDelay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_pulsedDelay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_pulsedDelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_continuousStart_2.setText(QCoreApplication.translate("Form", "Start", None))
        self.lineEdit_pulsedStart.setText(QCoreApplication.translate("Form", "0", None))
        self.label_pulsedStartUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_continuousEnd_2.setText(QCoreApplication.translate("Form", "End", None))
        self.lineEdit_pulsedEnd.setText(QCoreApplication.translate("Form", "0", None))
        self.label_pulsedEndUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_pulsedPoints.setText(QCoreApplication.translate("Form", "Points", None))
        self.lineEdit_pulsedPoints.setText(QCoreApplication.translate("Form", "1", None))
        self.label_continuousLimit_2.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_pulsedLimit.setText(QCoreApplication.translate("Form", "0", None))
        self.label_pulsedLimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_pulsedNPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_pulsedNPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_pulsedNPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_pulsedPause_2.setText(QCoreApplication.translate("Form", "Pause", None))
        self.lineEdit_pulsedPause.setText(QCoreApplication.translate("Form", "1", None))
        self.label_pulsedPause.setText(QCoreApplication.translate("Form", "s", None))
        self.groupBox_drainSweep.setTitle(QCoreApplication.translate("Form", "Drain", None))
        self.label_drainStart.setText(QCoreApplication.translate("Form", "Start", None))
        self.lineEdit_drainStart.setText(QCoreApplication.translate("Form", "0", None))
        self.label_drainStartUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_drainEnd.setText(QCoreApplication.translate("Form", "End", None))
        self.lineEdit_drainEnd.setText(QCoreApplication.translate("Form", "0", None))
        self.label_drainEndUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_drainPoints.setText(QCoreApplication.translate("Form", "Points", None))
        self.lineEdit_drainPoints.setText(QCoreApplication.translate("Form", "0", None))
        self.label_drainLimit.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_drainLimit.setText(QCoreApplication.translate("Form", "0", None))
        self.label_drainLimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_drainNPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_drainNPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_drainNPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_drainDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_drainDelayMode.setItemText(0, QCoreApplication.translate("Form", "Auto", None))
        self.comboBox_drainDelayMode.setItemText(1, QCoreApplication.translate("Form", "Manual", None))

        self.label_drainDelay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_drainDelay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_drainDelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_drainSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_drainSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_drainSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_drainSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.groupBox.setTitle("")
        self.label_plotUpdate.setText(QCoreApplication.translate("Form", "Plot update interval", None))
        self.label_plotUpdateUnit.setText(QCoreApplication.translate("Form", "s", None))
        self.labelPrescaler.setText(QCoreApplication.translate("Form", "SMU limit prescaler", None))
        self.prescalerEdit.setText(QCoreApplication.translate("Form", "1", None))
        self.fileBox.setTitle("")
        self.pathLabel.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select directory", None))
        self.filenameLabel.setText(QCoreApplication.translate("Form", "Filename", None))
        self.sampleName_label.setText(QCoreApplication.translate("Form", "Sample name", None))
        self.label_comment.setText(QCoreApplication.translate("Form", "Comment", None))
        self.buttonBox.setTitle("")
        self.runButton.setText(QCoreApplication.translate("Form", "Run", None))
        self.stopButton.setText(QCoreApplication.translate("Form", "Stop", None))

    # retranslateUi
