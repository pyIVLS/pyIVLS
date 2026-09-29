################################################################################
## Form generated from reading UI file 'fastPulse_settingsWidget.ui'
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
        Form.resize(860, 1022)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 840, 1002))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_dependency = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_dependency.setObjectName("groupBox_dependency")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_dependency)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QLabel(self.groupBox_dependency)
        self.label.setObjectName("label")

        self.horizontalLayout_4.addWidget(self.label)

        self.smuBox = QComboBox(self.groupBox_dependency)
        self.smuBox.setObjectName("smuBox")

        self.horizontalLayout_4.addWidget(self.smuBox)

        self.verticalLayout_6.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.applyDependencies = QPushButton(self.groupBox_dependency)
        self.applyDependencies.setObjectName("applyDependencies")

        self.horizontalLayout_6.addWidget(self.applyDependencies)

        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.verticalLayout_4.addWidget(self.groupBox_dependency)

        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_general_2 = QGroupBox(self.groupBox_general)
        self.groupBox_general_2.setObjectName("groupBox_general_2")
        self.groupBox_general_2.setMinimumSize(QSize(0, 0))
        self.groupBox_general_2.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_general_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.HBoxLayout_general = QHBoxLayout()
        self.HBoxLayout_general.setObjectName("HBoxLayout_general")
        self.HBoxLayout_channel = QHBoxLayout()
        self.HBoxLayout_channel.setObjectName("HBoxLayout_channel")
        self.label_Channel = QLabel(self.groupBox_general_2)
        self.label_Channel.setObjectName("label_Channel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_Channel.sizePolicy().hasHeightForWidth())
        self.label_Channel.setSizePolicy(sizePolicy1)
        self.label_Channel.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_channel.addWidget(self.label_Channel)

        self.comboBox_channel = QComboBox(self.groupBox_general_2)
        self.comboBox_channel.addItem("")
        self.comboBox_channel.addItem("")
        self.comboBox_channel.setObjectName("comboBox_channel")
        sizePolicy1.setHeightForWidth(self.comboBox_channel.sizePolicy().hasHeightForWidth())
        self.comboBox_channel.setSizePolicy(sizePolicy1)
        self.comboBox_channel.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_channel.addWidget(self.comboBox_channel)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_channel.addItem(self.horizontalSpacer_4)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_channel)

        self.HBoxLayout_inject = QHBoxLayout()
        self.HBoxLayout_inject.setObjectName("HBoxLayout_inject")
        self.label_inject = QLabel(self.groupBox_general_2)
        self.label_inject.setObjectName("label_inject")
        sizePolicy1.setHeightForWidth(self.label_inject.sizePolicy().hasHeightForWidth())
        self.label_inject.setSizePolicy(sizePolicy1)
        self.label_inject.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_inject.addWidget(self.label_inject)

        self.comboBox_inject = QComboBox(self.groupBox_general_2)
        self.comboBox_inject.addItem("")
        self.comboBox_inject.addItem("")
        self.comboBox_inject.setObjectName("comboBox_inject")
        sizePolicy1.setHeightForWidth(self.comboBox_inject.sizePolicy().hasHeightForWidth())
        self.comboBox_inject.setSizePolicy(sizePolicy1)
        self.comboBox_inject.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_inject.addWidget(self.comboBox_inject)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_inject.addItem(self.horizontalSpacer_5)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_inject)

        self.HBoxLayout_mode = QHBoxLayout()
        self.HBoxLayout_mode.setObjectName("HBoxLayout_mode")
        self.label_mode = QLabel(self.groupBox_general_2)
        self.label_mode.setObjectName("label_mode")
        sizePolicy1.setHeightForWidth(self.label_mode.sizePolicy().hasHeightForWidth())
        self.label_mode.setSizePolicy(sizePolicy1)
        self.label_mode.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_mode.addWidget(self.label_mode)

        self.comboBox_mode = QComboBox(self.groupBox_general_2)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName("comboBox_mode")
        sizePolicy1.setHeightForWidth(self.comboBox_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_mode.setSizePolicy(sizePolicy1)
        self.comboBox_mode.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_mode.addWidget(self.comboBox_mode)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_mode.addItem(self.horizontalSpacer_6)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_mode)

        self.HBoxLayout_sourceSenseMode = QHBoxLayout()
        self.HBoxLayout_sourceSenseMode.setObjectName("HBoxLayout_sourceSenseMode")
        self.label_sourceSenseMode = QLabel(self.groupBox_general_2)
        self.label_sourceSenseMode.setObjectName("label_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.label_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.label_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.label_sourceSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.label_sourceSenseMode)

        self.comboBox_sourceSenseMode = QComboBox(self.groupBox_general_2)
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.setObjectName("comboBox_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.comboBox_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.comboBox_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.comboBox_sourceSenseMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.comboBox_sourceSenseMode)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceSenseMode.addItem(self.horizontalSpacer_7)

        self.HBoxLayout_general.addLayout(self.HBoxLayout_sourceSenseMode)

        self.horizontalSpacer1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_general.addItem(self.horizontalSpacer1)

        self.HBoxLayout_general.setStretch(0, 10)
        self.HBoxLayout_general.setStretch(1, 10)
        self.HBoxLayout_general.setStretch(2, 10)
        self.HBoxLayout_general.setStretch(3, 10)

        self.verticalLayout_2.addLayout(self.HBoxLayout_general)

        self.HBoxLayout_singleChannel = QHBoxLayout()
        self.HBoxLayout_singleChannel.setObjectName("HBoxLayout_singleChannel")
        self.label_6 = QLabel(self.groupBox_general_2)
        self.label_6.setObjectName("label_6")

        self.HBoxLayout_singleChannel.addWidget(self.label_6)

        self.lineEdit_drainValue = QLineEdit(self.groupBox_general_2)
        self.lineEdit_drainValue.setObjectName("lineEdit_drainValue")
        self.lineEdit_drainValue.setMaximumSize(QSize(100, 100))

        self.HBoxLayout_singleChannel.addWidget(self.lineEdit_drainValue)

        self.label_7 = QLabel(self.groupBox_general_2)
        self.label_7.setObjectName("label_7")

        self.HBoxLayout_singleChannel.addWidget(self.label_7)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_singleChannel.addItem(self.horizontalSpacer_8)

        self.checkBox_useTimeAfter = QCheckBox(self.groupBox_general_2)
        self.checkBox_useTimeAfter.setObjectName("checkBox_useTimeAfter")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_useTimeAfter)

        self.lineEdit_timeAfter = QLineEdit(self.groupBox_general_2)
        self.lineEdit_timeAfter.setObjectName("lineEdit_timeAfter")
        self.lineEdit_timeAfter.setMaximumSize(QSize(100, 16777215))

        self.HBoxLayout_singleChannel.addWidget(self.lineEdit_timeAfter)

        self.label_8 = QLabel(self.groupBox_general_2)
        self.label_8.setObjectName("label_8")

        self.HBoxLayout_singleChannel.addWidget(self.label_8)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_singleChannel.addItem(self.horizontalSpacer_10)

        self.checkBox_singleChannel = QCheckBox(self.groupBox_general_2)
        self.checkBox_singleChannel.setObjectName("checkBox_singleChannel")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_singleChannel)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_singleChannel.addItem(self.horizontalSpacer_9)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_5 = QLabel(self.groupBox_general_2)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_7.addWidget(self.label_5)

        self.prescalerSpinBox = QDoubleSpinBox(self.groupBox_general_2)
        self.prescalerSpinBox.setObjectName("prescalerSpinBox")
        self.prescalerSpinBox.setMaximum(1.000000000000000)
        self.prescalerSpinBox.setSingleStep(0.100000000000000)
        self.prescalerSpinBox.setValue(1.000000000000000)

        self.horizontalLayout_7.addWidget(self.prescalerSpinBox)

        self.HBoxLayout_singleChannel.addLayout(self.horizontalLayout_7)

        self.verticalLayout_2.addLayout(self.HBoxLayout_singleChannel)

        self.verticalLayout.addWidget(self.groupBox_general_2)

        self.groupBox_control = QGroupBox(self.groupBox_general)
        self.groupBox_control.setObjectName("groupBox_control")
        self.groupBox_control.setEnabled(True)
        self.groupBox_control.setMinimumSize(QSize(0, 0))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_control)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.HBoxLayout_pulsedLine1 = QHBoxLayout()
        self.HBoxLayout_pulsedLine1.setObjectName("HBoxLayout_pulsedLine1")
        self.HBoxLayout_pulsedStart = QHBoxLayout()
        self.HBoxLayout_pulsedStart.setObjectName("HBoxLayout_pulsedStart")
        self.label_Start = QLabel(self.groupBox_control)
        self.label_Start.setObjectName("label_Start")
        sizePolicy1.setHeightForWidth(self.label_Start.sizePolicy().hasHeightForWidth())
        self.label_Start.setSizePolicy(sizePolicy1)
        self.label_Start.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.label_Start)

        self.lineEdit_Start = QLineEdit(self.groupBox_control)
        self.lineEdit_Start.setObjectName("lineEdit_Start")
        sizePolicy1.setHeightForWidth(self.lineEdit_Start.sizePolicy().hasHeightForWidth())
        self.lineEdit_Start.setSizePolicy(sizePolicy1)
        self.lineEdit_Start.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.lineEdit_Start)

        self.label_StartUnits = QLabel(self.groupBox_control)
        self.label_StartUnits.setObjectName("label_StartUnits")

        self.HBoxLayout_pulsedStart.addWidget(self.label_StartUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedStart)

        self.HBoxLayout_pulsedEnd = QHBoxLayout()
        self.HBoxLayout_pulsedEnd.setObjectName("HBoxLayout_pulsedEnd")
        self.label_End = QLabel(self.groupBox_control)
        self.label_End.setObjectName("label_End")
        sizePolicy1.setHeightForWidth(self.label_End.sizePolicy().hasHeightForWidth())
        self.label_End.setSizePolicy(sizePolicy1)
        self.label_End.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.label_End)

        self.lineEdit_End = QLineEdit(self.groupBox_control)
        self.lineEdit_End.setObjectName("lineEdit_End")
        sizePolicy1.setHeightForWidth(self.lineEdit_End.sizePolicy().hasHeightForWidth())
        self.lineEdit_End.setSizePolicy(sizePolicy1)
        self.lineEdit_End.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.lineEdit_End)

        self.label_EndUnits = QLabel(self.groupBox_control)
        self.label_EndUnits.setObjectName("label_EndUnits")

        self.HBoxLayout_pulsedEnd.addWidget(self.label_EndUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedEnd)

        self.HBoxLayout_pulsedPoints = QHBoxLayout()
        self.HBoxLayout_pulsedPoints.setObjectName("HBoxLayout_pulsedPoints")
        self.label_Points = QLabel(self.groupBox_control)
        self.label_Points.setObjectName("label_Points")
        sizePolicy1.setHeightForWidth(self.label_Points.sizePolicy().hasHeightForWidth())
        self.label_Points.setSizePolicy(sizePolicy1)
        self.label_Points.setMinimumSize(QSize(50, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.label_Points)

        self.lineEdit_Points = QLineEdit(self.groupBox_control)
        self.lineEdit_Points.setObjectName("lineEdit_Points")
        sizePolicy1.setHeightForWidth(self.lineEdit_Points.sizePolicy().hasHeightForWidth())
        self.lineEdit_Points.setSizePolicy(sizePolicy1)
        self.lineEdit_Points.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.lineEdit_Points)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPoints)

        self.HBoxLayout_pulsedLimit = QHBoxLayout()
        self.HBoxLayout_pulsedLimit.setObjectName("HBoxLayout_pulsedLimit")
        self.label_Limit = QLabel(self.groupBox_control)
        self.label_Limit.setObjectName("label_Limit")
        sizePolicy1.setHeightForWidth(self.label_Limit.sizePolicy().hasHeightForWidth())
        self.label_Limit.setSizePolicy(sizePolicy1)
        self.label_Limit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.label_Limit)

        self.lineEdit_Limit = QLineEdit(self.groupBox_control)
        self.lineEdit_Limit.setObjectName("lineEdit_Limit")
        sizePolicy1.setHeightForWidth(self.lineEdit_Limit.sizePolicy().hasHeightForWidth())
        self.lineEdit_Limit.setSizePolicy(sizePolicy1)
        self.lineEdit_Limit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.lineEdit_Limit)

        self.label_LimitUnits = QLabel(self.groupBox_control)
        self.label_LimitUnits.setObjectName("label_LimitUnits")

        self.HBoxLayout_pulsedLimit.addWidget(self.label_LimitUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedLimit)

        self.HBoxLayout_pulsedPause = QHBoxLayout()
        self.HBoxLayout_pulsedPause.setObjectName("HBoxLayout_pulsedPause")
        self.label_pulsedPause_2 = QLabel(self.groupBox_control)
        self.label_pulsedPause_2.setObjectName("label_pulsedPause_2")
        sizePolicy1.setHeightForWidth(self.label_pulsedPause_2.sizePolicy().hasHeightForWidth())
        self.label_pulsedPause_2.setSizePolicy(sizePolicy1)
        self.label_pulsedPause_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause_2)

        self.lineEdit_Pause = QLineEdit(self.groupBox_control)
        self.lineEdit_Pause.setObjectName("lineEdit_Pause")
        sizePolicy1.setHeightForWidth(self.lineEdit_Pause.sizePolicy().hasHeightForWidth())
        self.lineEdit_Pause.setSizePolicy(sizePolicy1)
        self.lineEdit_Pause.setMinimumSize(QSize(20, 0))
        self.lineEdit_Pause.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.lineEdit_Pause)

        self.label_pulsedPause = QLabel(self.groupBox_control)
        self.label_pulsedPause.setObjectName("label_pulsedPause")

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPause)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_pulsedLine1.addItem(self.horizontalSpacer_3)

        self.HBoxLayout_pulsedLine1.setStretch(1, 10)
        self.HBoxLayout_pulsedLine1.setStretch(2, 10)
        self.HBoxLayout_pulsedLine1.setStretch(3, 10)
        self.HBoxLayout_pulsedLine1.setStretch(4, 10)

        self.verticalLayout_5.addLayout(self.HBoxLayout_pulsedLine1)

        self.HBoxLayout_pulsedLine2 = QHBoxLayout()
        self.HBoxLayout_pulsedLine2.setObjectName("HBoxLayout_pulsedLine2")
        self.HBoxLayout_pulsedDelayMode = QHBoxLayout()
        self.HBoxLayout_pulsedDelayMode.setObjectName("HBoxLayout_pulsedDelayMode")
        self.label_NPLC = QLabel(self.groupBox_control)
        self.label_NPLC.setObjectName("label_NPLC")
        sizePolicy1.setHeightForWidth(self.label_NPLC.sizePolicy().hasHeightForWidth())
        self.label_NPLC.setSizePolicy(sizePolicy1)
        self.label_NPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.label_NPLC)

        self.lineEdit_NPLC = QLineEdit(self.groupBox_control)
        self.lineEdit_NPLC.setObjectName("lineEdit_NPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_NPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_NPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_NPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_NPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.lineEdit_NPLC)

        self.label_NPLCUnits = QLabel(self.groupBox_control)
        self.label_NPLCUnits.setObjectName("label_NPLCUnits")

        self.HBoxLayout_pulsedDelayMode.addWidget(self.label_NPLCUnits)

        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelayMode)

        self.HBoxLayout_pulsedDelay = QHBoxLayout()
        self.HBoxLayout_pulsedDelay.setObjectName("HBoxLayout_pulsedDelay")
        self.label_Delay = QLabel(self.groupBox_control)
        self.label_Delay.setObjectName("label_Delay")
        sizePolicy1.setHeightForWidth(self.label_Delay.sizePolicy().hasHeightForWidth())
        self.label_Delay.setSizePolicy(sizePolicy1)
        self.label_Delay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.label_Delay)

        self.lineEdit_pulseTime = QLineEdit(self.groupBox_control)
        self.lineEdit_pulseTime.setObjectName("lineEdit_pulseTime")
        sizePolicy1.setHeightForWidth(self.lineEdit_pulseTime.sizePolicy().hasHeightForWidth())
        self.lineEdit_pulseTime.setSizePolicy(sizePolicy1)
        self.lineEdit_pulseTime.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.lineEdit_pulseTime)

        self.label_DelayUnits = QLabel(self.groupBox_control)
        self.label_DelayUnits.setObjectName("label_DelayUnits")

        self.HBoxLayout_pulsedDelay.addWidget(self.label_DelayUnits)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QLabel(self.groupBox_control)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.repeat_spinbox = QSpinBox(self.groupBox_control)
        self.repeat_spinbox.setObjectName("repeat_spinbox")
        self.repeat_spinbox.setMinimum(1)

        self.horizontalLayout_3.addWidget(self.repeat_spinbox)

        self.HBoxLayout_pulsedDelay.addLayout(self.horizontalLayout_3)

        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelay)

        self.HBoxLayout_pulsedLine2.setStretch(0, 10)
        self.HBoxLayout_pulsedLine2.setStretch(1, 10)

        self.verticalLayout_5.addLayout(self.HBoxLayout_pulsedLine2)

        self.verticalLayout.addWidget(self.groupBox_control)

        self.verticalLayout_4.addWidget(self.groupBox_general)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_path = QLabel(self.groupBox)
        self.label_path.setObjectName("label_path")
        self.label_path.setMaximumSize(QSize(150, 16777215))

        self.gridLayout_3.addWidget(self.label_path, 0, 0, 1, 1)

        self.lineEdit_path = QLineEdit(self.groupBox)
        self.lineEdit_path.setObjectName("lineEdit_path")
        self.lineEdit_path.setMaximumSize(QSize(1000, 16777215))

        self.gridLayout_3.addWidget(self.lineEdit_path, 0, 2, 1, 1)

        self.lineEdit_filename = QLineEdit(self.groupBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")

        self.gridLayout_3.addWidget(self.lineEdit_filename, 1, 2, 1, 1)

        self.label_sample = QLabel(self.groupBox)
        self.label_sample.setObjectName("label_sample")

        self.gridLayout_3.addWidget(self.label_sample, 2, 0, 1, 1)

        self.directoryButton = QPushButton(self.groupBox)
        self.directoryButton.setObjectName("directoryButton")
        self.directoryButton.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_3.addWidget(self.directoryButton, 0, 4, 1, 1)

        self.label_filename = QLabel(self.groupBox)
        self.label_filename.setObjectName("label_filename")
        self.label_filename.setMaximumSize(QSize(100, 16777215))

        self.gridLayout_3.addWidget(self.label_filename, 1, 0, 1, 1)

        self.lineEdit_sampleName = QLineEdit(self.groupBox)
        self.lineEdit_sampleName.setObjectName("lineEdit_sampleName")

        self.gridLayout_3.addWidget(self.lineEdit_sampleName, 2, 2, 1, 1)

        self.label_comment = QLabel(self.groupBox)
        self.label_comment.setObjectName("label_comment")

        self.gridLayout_3.addWidget(self.label_comment, 3, 0, 1, 1)

        self.lineEdit_comment = QLineEdit(self.groupBox)
        self.lineEdit_comment.setObjectName("lineEdit_comment")

        self.gridLayout_3.addWidget(self.lineEdit_comment, 3, 2, 1, 1)

        self.verticalLayout_8.addLayout(self.gridLayout_3)

        self.verticalLayout_4.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        self.comboBox_channel.setCurrentIndex(-1)
        self.comboBox_inject.setCurrentIndex(0)
        self.comboBox_mode.setCurrentIndex(0)
        self.comboBox_sourceSenseMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "SpecSMU_settings", None))
        self.groupBox_dependency.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.label.setText(QCoreApplication.translate("Form", "SMU Plugin", None))
        self.applyDependencies.setText(QCoreApplication.translate("Form", "Apply dependencies", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "SMU settings", None))
        self.groupBox_general_2.setTitle(QCoreApplication.translate("Form", "General", None))
        self.label_Channel.setText(QCoreApplication.translate("Form", "Source channel", None))
        self.comboBox_channel.setItemText(0, QCoreApplication.translate("Form", "smuA", None))
        self.comboBox_channel.setItemText(1, QCoreApplication.translate("Form", "smuB", None))

        self.label_inject.setText(QCoreApplication.translate("Form", "Inject", None))
        self.comboBox_inject.setItemText(0, QCoreApplication.translate("Form", "Current", None))
        self.comboBox_inject.setItemText(1, QCoreApplication.translate("Form", "Voltage", None))

        self.label_mode.setText(QCoreApplication.translate("Form", "Mode", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("Form", "Continuous", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("Form", "Pulsed", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Form", "HW trigger", None))

        self.label_sourceSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_sourceSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_sourceSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_sourceSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.label_6.setText(QCoreApplication.translate("Form", "Drain voltage", None))
        self.lineEdit_drainValue.setText(QCoreApplication.translate("Form", "0", None))
        self.label_7.setText(QCoreApplication.translate("Form", "V", None))
        self.checkBox_useTimeAfter.setText(QCoreApplication.translate("Form", "Additional time", None))
        self.label_8.setText(QCoreApplication.translate("Form", "ms", None))
        self.checkBox_singleChannel.setText(QCoreApplication.translate("Form", "Use single channel", None))
        self.label_5.setText(QCoreApplication.translate("Form", "Prescaler", None))
        self.groupBox_control.setTitle(QCoreApplication.translate("Form", "SMU Control", None))
        self.label_Start.setText(QCoreApplication.translate("Form", "Start", None))
        self.lineEdit_Start.setText(QCoreApplication.translate("Form", "0", None))
        self.label_StartUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_End.setText(QCoreApplication.translate("Form", "End", None))
        self.lineEdit_End.setText(QCoreApplication.translate("Form", "0", None))
        self.label_EndUnits.setText(QCoreApplication.translate("Form", "A", None))
        self.label_Points.setText(QCoreApplication.translate("Form", "Points", None))
        self.lineEdit_Points.setText(QCoreApplication.translate("Form", "1", None))
        self.label_Limit.setText(QCoreApplication.translate("Form", "Limit", None))
        self.lineEdit_Limit.setText(QCoreApplication.translate("Form", "0", None))
        self.label_LimitUnits.setText(QCoreApplication.translate("Form", "V", None))
        self.label_pulsedPause_2.setText(QCoreApplication.translate("Form", "Pause", None))
        self.lineEdit_Pause.setText(QCoreApplication.translate("Form", "1", None))
        self.label_pulsedPause.setText(QCoreApplication.translate("Form", "s", None))
        self.label_NPLC.setText(QCoreApplication.translate("Form", "Sample time", None))
        self.lineEdit_NPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_NPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_Delay.setText(QCoreApplication.translate("Form", "Pulse time", None))
        self.lineEdit_pulseTime.setText(QCoreApplication.translate("Form", "10", None))
        self.label_DelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Repeat", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", "Saving", None))
        self.label_path.setText(QCoreApplication.translate("Form", "Path to save", None))
        self.label_sample.setText(QCoreApplication.translate("Form", "Sample name", None))
        self.directoryButton.setText(QCoreApplication.translate("Form", "Select", None))
        self.label_filename.setText(QCoreApplication.translate("Form", "Filename", None))
        self.label_comment.setText(QCoreApplication.translate("Form", "Comment", None))

    # retranslateUi
