# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'specSMU_settingsWidgetKXkfLk.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1566, 1050)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1546, 1030))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_dependency = QGroupBox(self.groupBox_general)
        self.groupBox_dependency.setObjectName("groupBox_dependency")
        self.gridLayout_2 = QGridLayout(self.groupBox_dependency)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.smuBox = QComboBox(self.groupBox_dependency)
        self.smuBox.setObjectName("smuBox")

        self.gridLayout_2.addWidget(self.smuBox, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_dependency)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_dependency)
        self.label_2.setObjectName("label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.spectrometerBox = QComboBox(self.groupBox_dependency)
        self.spectrometerBox.setObjectName("spectrometerBox")

        self.gridLayout_2.addWidget(self.spectrometerBox, 1, 1, 1, 1)

        self.verticalLayout.addWidget(self.groupBox_dependency)

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

        self.HBoxLayout_general.addLayout(self.HBoxLayout_sourceSenseMode)

        self.HBoxLayout_general.setStretch(0, 10)
        self.HBoxLayout_general.setStretch(1, 10)
        self.HBoxLayout_general.setStretch(2, 10)
        self.HBoxLayout_general.setStretch(3, 10)

        self.verticalLayout_2.addLayout(self.HBoxLayout_general)

        self.HBoxLayout_singleChannel = QHBoxLayout()
        self.HBoxLayout_singleChannel.setObjectName("HBoxLayout_singleChannel")
        self.checkBox_singleChannel = QCheckBox(self.groupBox_general_2)
        self.checkBox_singleChannel.setObjectName("checkBox_singleChannel")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_singleChannel)

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

        self.HBoxLayout_pulsedNPLC = QHBoxLayout()
        self.HBoxLayout_pulsedNPLC.setObjectName("HBoxLayout_pulsedNPLC")
        self.label_NPLC = QLabel(self.groupBox_control)
        self.label_NPLC.setObjectName("label_NPLC")
        sizePolicy1.setHeightForWidth(self.label_NPLC.sizePolicy().hasHeightForWidth())
        self.label_NPLC.setSizePolicy(sizePolicy1)
        self.label_NPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_NPLC)

        self.lineEdit_NPLC = QLineEdit(self.groupBox_control)
        self.lineEdit_NPLC.setObjectName("lineEdit_NPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_NPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_NPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_NPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_NPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.lineEdit_NPLC)

        self.label_NPLCUnits = QLabel(self.groupBox_control)
        self.label_NPLCUnits.setObjectName("label_NPLCUnits")

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_NPLCUnits)

        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedNPLC)

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

        self.HBoxLayout_pulsedLine1.setStretch(1, 10)
        self.HBoxLayout_pulsedLine1.setStretch(2, 10)
        self.HBoxLayout_pulsedLine1.setStretch(3, 10)
        self.HBoxLayout_pulsedLine1.setStretch(4, 10)
        self.HBoxLayout_pulsedLine1.setStretch(5, 10)

        self.verticalLayout_5.addLayout(self.HBoxLayout_pulsedLine1)

        self.HBoxLayout_pulsedLine2 = QHBoxLayout()
        self.HBoxLayout_pulsedLine2.setObjectName("HBoxLayout_pulsedLine2")
        self.HBoxLayout_pulsedDelayMode = QHBoxLayout()
        self.HBoxLayout_pulsedDelayMode.setObjectName("HBoxLayout_pulsedDelayMode")
        self.label_pulsedDelayMode = QLabel(self.groupBox_control)
        self.label_pulsedDelayMode.setObjectName("label_pulsedDelayMode")
        sizePolicy1.setHeightForWidth(self.label_pulsedDelayMode.sizePolicy().hasHeightForWidth())
        self.label_pulsedDelayMode.setSizePolicy(sizePolicy1)
        self.label_pulsedDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.label_pulsedDelayMode)

        self.comboBox_DelayMode = QComboBox(self.groupBox_control)
        self.comboBox_DelayMode.addItem("")
        self.comboBox_DelayMode.addItem("")
        self.comboBox_DelayMode.setObjectName("comboBox_DelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_DelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_DelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_DelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.comboBox_DelayMode)

        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelayMode)

        self.HBoxLayout_pulsedDelay = QHBoxLayout()
        self.HBoxLayout_pulsedDelay.setObjectName("HBoxLayout_pulsedDelay")
        self.label_Delay = QLabel(self.groupBox_control)
        self.label_Delay.setObjectName("label_Delay")
        sizePolicy1.setHeightForWidth(self.label_Delay.sizePolicy().hasHeightForWidth())
        self.label_Delay.setSizePolicy(sizePolicy1)
        self.label_Delay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.label_Delay)

        self.lineEdit_Delay = QLineEdit(self.groupBox_control)
        self.lineEdit_Delay.setObjectName("lineEdit_Delay")
        sizePolicy1.setHeightForWidth(self.lineEdit_Delay.sizePolicy().hasHeightForWidth())
        self.lineEdit_Delay.setSizePolicy(sizePolicy1)
        self.lineEdit_Delay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.lineEdit_Delay)

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

        self.groupBox = QGroupBox(self.groupBox_general)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.spectroCheckAfter = QCheckBox(self.groupBox)
        self.spectroCheckAfter.setObjectName("spectroCheckAfter")

        self.horizontalLayout_2.addWidget(self.spectroCheckAfter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spectroPause = QCheckBox(self.groupBox)
        self.spectroPause.setObjectName("spectroPause")

        self.horizontalLayout.addWidget(self.spectroPause)

        self.spectroPauseSpinBox = QDoubleSpinBox(self.groupBox)
        self.spectroPauseSpinBox.setObjectName("spectroPauseSpinBox")
        self.spectroPauseSpinBox.setMaximum(15.000000000000000)
        self.spectroPauseSpinBox.setSingleStep(0.500000000000000)

        self.horizontalLayout.addWidget(self.spectroPauseSpinBox)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.spectroUseLastInteg = QCheckBox(self.groupBox)
        self.spectroUseLastInteg.setObjectName("spectroUseLastInteg")

        self.horizontalLayout_2.addWidget(self.spectroUseLastInteg)

        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_4.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        self.comboBox_channel.setCurrentIndex(0)
        self.comboBox_inject.setCurrentIndex(0)
        self.comboBox_mode.setCurrentIndex(0)
        self.comboBox_sourceSenseMode.setCurrentIndex(0)
        self.comboBox_DelayMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "SpecSMU_settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "SMU settings", None))
        self.groupBox_dependency.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.label.setText(QCoreApplication.translate("Form", "SMU Plugin", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Spectrometer Plugin", None))
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
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Form", "Mixed", None))

        self.label_sourceSenseMode.setText(QCoreApplication.translate("Form", "Sense", None))
        self.comboBox_sourceSenseMode.setItemText(0, QCoreApplication.translate("Form", "2 wire", None))
        self.comboBox_sourceSenseMode.setItemText(1, QCoreApplication.translate("Form", "4 wire", None))
        self.comboBox_sourceSenseMode.setItemText(2, QCoreApplication.translate("Form", "2 & 4 wire", None))

        self.checkBox_singleChannel.setText(QCoreApplication.translate("Form", "Use single channel", None))
        self.groupBox_control.setTitle(QCoreApplication.translate("Form", "Control", None))
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
        self.label_NPLC.setText(QCoreApplication.translate("Form", "NPLC", None))
        self.lineEdit_NPLC.setText(QCoreApplication.translate("Form", "1", None))
        self.label_NPLCUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_pulsedPause_2.setText(QCoreApplication.translate("Form", "Pause", None))
        self.lineEdit_Pause.setText(QCoreApplication.translate("Form", "1", None))
        self.label_pulsedPause.setText(QCoreApplication.translate("Form", "s", None))
        self.label_pulsedDelayMode.setText(QCoreApplication.translate("Form", "Delay mode", None))
        self.comboBox_DelayMode.setItemText(0, QCoreApplication.translate("Form", "Auto", None))
        self.comboBox_DelayMode.setItemText(1, QCoreApplication.translate("Form", "Manual", None))

        self.label_Delay.setText(QCoreApplication.translate("Form", "Delay", None))
        self.lineEdit_Delay.setText(QCoreApplication.translate("Form", "10", None))
        self.label_DelayUnits.setText(QCoreApplication.translate("Form", "ms", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Repeat", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", "Spectrometer", None))
        self.spectroCheckAfter.setText(QCoreApplication.translate("Form", "Measure IV before and after", None))
        self.spectroPause.setText(QCoreApplication.translate("Form", "pause", None))
        self.spectroUseLastInteg.setText(QCoreApplication.translate("Form", "getAutoTime initial guess from last integration time", None))

    # retranslateUi
