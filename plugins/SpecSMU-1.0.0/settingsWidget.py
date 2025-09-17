# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'specSMU_settingsWidgetZnsTSV.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PyQt6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QDoubleSpinBox


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1560, 1037)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1540, 1017))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName(u"groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_dependency = QGroupBox(self.groupBox_general)
        self.groupBox_dependency.setObjectName(u"groupBox_dependency")
        self.gridLayout_2 = QGridLayout(self.groupBox_dependency)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.smuBox = QComboBox(self.groupBox_dependency)
        self.smuBox.setObjectName(u"smuBox")

        self.gridLayout_2.addWidget(self.smuBox, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_dependency)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_dependency)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.spectrometerBox = QComboBox(self.groupBox_dependency)
        self.spectrometerBox.setObjectName(u"spectrometerBox")

        self.gridLayout_2.addWidget(self.spectrometerBox, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_dependency)

        self.groupBox_general_2 = QGroupBox(self.groupBox_general)
        self.groupBox_general_2.setObjectName(u"groupBox_general_2")
        self.groupBox_general_2.setMinimumSize(QSize(0, 0))
        self.groupBox_general_2.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_general_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.HBoxLayout_general = QHBoxLayout()
        self.HBoxLayout_general.setObjectName(u"HBoxLayout_general")
        self.HBoxLayout_channel = QHBoxLayout()
        self.HBoxLayout_channel.setObjectName(u"HBoxLayout_channel")
        self.label_Channel = QLabel(self.groupBox_general_2)
        self.label_Channel.setObjectName(u"label_Channel")
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
        self.comboBox_channel.setObjectName(u"comboBox_channel")
        sizePolicy1.setHeightForWidth(self.comboBox_channel.sizePolicy().hasHeightForWidth())
        self.comboBox_channel.setSizePolicy(sizePolicy1)
        self.comboBox_channel.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_channel.addWidget(self.comboBox_channel)


        self.HBoxLayout_general.addLayout(self.HBoxLayout_channel)

        self.HBoxLayout_inject = QHBoxLayout()
        self.HBoxLayout_inject.setObjectName(u"HBoxLayout_inject")
        self.label_inject = QLabel(self.groupBox_general_2)
        self.label_inject.setObjectName(u"label_inject")
        sizePolicy1.setHeightForWidth(self.label_inject.sizePolicy().hasHeightForWidth())
        self.label_inject.setSizePolicy(sizePolicy1)
        self.label_inject.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_inject.addWidget(self.label_inject)

        self.comboBox_inject = QComboBox(self.groupBox_general_2)
        self.comboBox_inject.addItem("")
        self.comboBox_inject.addItem("")
        self.comboBox_inject.setObjectName(u"comboBox_inject")
        sizePolicy1.setHeightForWidth(self.comboBox_inject.sizePolicy().hasHeightForWidth())
        self.comboBox_inject.setSizePolicy(sizePolicy1)
        self.comboBox_inject.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_inject.addWidget(self.comboBox_inject)


        self.HBoxLayout_general.addLayout(self.HBoxLayout_inject)

        self.HBoxLayout_mode = QHBoxLayout()
        self.HBoxLayout_mode.setObjectName(u"HBoxLayout_mode")
        self.label_mode = QLabel(self.groupBox_general_2)
        self.label_mode.setObjectName(u"label_mode")
        sizePolicy1.setHeightForWidth(self.label_mode.sizePolicy().hasHeightForWidth())
        self.label_mode.setSizePolicy(sizePolicy1)
        self.label_mode.setMinimumSize(QSize(60, 0))

        self.HBoxLayout_mode.addWidget(self.label_mode)

        self.comboBox_mode = QComboBox(self.groupBox_general_2)
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.addItem("")
        self.comboBox_mode.setObjectName(u"comboBox_mode")
        sizePolicy1.setHeightForWidth(self.comboBox_mode.sizePolicy().hasHeightForWidth())
        self.comboBox_mode.setSizePolicy(sizePolicy1)
        self.comboBox_mode.setMinimumSize(QSize(120, 0))

        self.HBoxLayout_mode.addWidget(self.comboBox_mode)


        self.HBoxLayout_general.addLayout(self.HBoxLayout_mode)

        self.HBoxLayout_sourceSenseMode = QHBoxLayout()
        self.HBoxLayout_sourceSenseMode.setObjectName(u"HBoxLayout_sourceSenseMode")
        self.label_sourceSenseMode = QLabel(self.groupBox_general_2)
        self.label_sourceSenseMode.setObjectName(u"label_sourceSenseMode")
        sizePolicy1.setHeightForWidth(self.label_sourceSenseMode.sizePolicy().hasHeightForWidth())
        self.label_sourceSenseMode.setSizePolicy(sizePolicy1)
        self.label_sourceSenseMode.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_sourceSenseMode.addWidget(self.label_sourceSenseMode)

        self.comboBox_sourceSenseMode = QComboBox(self.groupBox_general_2)
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.addItem("")
        self.comboBox_sourceSenseMode.setObjectName(u"comboBox_sourceSenseMode")
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
        self.HBoxLayout_singleChannel.setObjectName(u"HBoxLayout_singleChannel")
        self.checkBox_singleChannel = QCheckBox(self.groupBox_general_2)
        self.checkBox_singleChannel.setObjectName(u"checkBox_singleChannel")

        self.HBoxLayout_singleChannel.addWidget(self.checkBox_singleChannel)


        self.verticalLayout_2.addLayout(self.HBoxLayout_singleChannel)


        self.verticalLayout.addWidget(self.groupBox_general_2)

        self.groupBox_control = QGroupBox(self.groupBox_general)
        self.groupBox_control.setObjectName(u"groupBox_control")
        self.groupBox_control.setEnabled(True)
        self.groupBox_control.setMinimumSize(QSize(0, 0))
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_control)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.HBoxLayout_pulsedLine1 = QHBoxLayout()
        self.HBoxLayout_pulsedLine1.setObjectName(u"HBoxLayout_pulsedLine1")
        self.HBoxLayout_pulsedStart = QHBoxLayout()
        self.HBoxLayout_pulsedStart.setObjectName(u"HBoxLayout_pulsedStart")
        self.label_Start = QLabel(self.groupBox_control)
        self.label_Start.setObjectName(u"label_Start")
        sizePolicy1.setHeightForWidth(self.label_Start.sizePolicy().hasHeightForWidth())
        self.label_Start.setSizePolicy(sizePolicy1)
        self.label_Start.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.label_Start)

        self.lineEdit_Start = QLineEdit(self.groupBox_control)
        self.lineEdit_Start.setObjectName(u"lineEdit_Start")
        sizePolicy1.setHeightForWidth(self.lineEdit_Start.sizePolicy().hasHeightForWidth())
        self.lineEdit_Start.setSizePolicy(sizePolicy1)
        self.lineEdit_Start.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedStart.addWidget(self.lineEdit_Start)

        self.label_StartUnits = QLabel(self.groupBox_control)
        self.label_StartUnits.setObjectName(u"label_StartUnits")

        self.HBoxLayout_pulsedStart.addWidget(self.label_StartUnits)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedStart)

        self.HBoxLayout_pulsedEnd = QHBoxLayout()
        self.HBoxLayout_pulsedEnd.setObjectName(u"HBoxLayout_pulsedEnd")
        self.label_End = QLabel(self.groupBox_control)
        self.label_End.setObjectName(u"label_End")
        sizePolicy1.setHeightForWidth(self.label_End.sizePolicy().hasHeightForWidth())
        self.label_End.setSizePolicy(sizePolicy1)
        self.label_End.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.label_End)

        self.lineEdit_End = QLineEdit(self.groupBox_control)
        self.lineEdit_End.setObjectName(u"lineEdit_End")
        sizePolicy1.setHeightForWidth(self.lineEdit_End.sizePolicy().hasHeightForWidth())
        self.lineEdit_End.setSizePolicy(sizePolicy1)
        self.lineEdit_End.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedEnd.addWidget(self.lineEdit_End)

        self.label_EndUnits = QLabel(self.groupBox_control)
        self.label_EndUnits.setObjectName(u"label_EndUnits")

        self.HBoxLayout_pulsedEnd.addWidget(self.label_EndUnits)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedEnd)

        self.HBoxLayout_pulsedPoints = QHBoxLayout()
        self.HBoxLayout_pulsedPoints.setObjectName(u"HBoxLayout_pulsedPoints")
        self.label_Points = QLabel(self.groupBox_control)
        self.label_Points.setObjectName(u"label_Points")
        sizePolicy1.setHeightForWidth(self.label_Points.sizePolicy().hasHeightForWidth())
        self.label_Points.setSizePolicy(sizePolicy1)
        self.label_Points.setMinimumSize(QSize(50, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.label_Points)

        self.lineEdit_Points = QLineEdit(self.groupBox_control)
        self.lineEdit_Points.setObjectName(u"lineEdit_Points")
        sizePolicy1.setHeightForWidth(self.lineEdit_Points.sizePolicy().hasHeightForWidth())
        self.lineEdit_Points.setSizePolicy(sizePolicy1)
        self.lineEdit_Points.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedPoints.addWidget(self.lineEdit_Points)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPoints)

        self.HBoxLayout_pulsedLimit = QHBoxLayout()
        self.HBoxLayout_pulsedLimit.setObjectName(u"HBoxLayout_pulsedLimit")
        self.label_Limit = QLabel(self.groupBox_control)
        self.label_Limit.setObjectName(u"label_Limit")
        sizePolicy1.setHeightForWidth(self.label_Limit.sizePolicy().hasHeightForWidth())
        self.label_Limit.setSizePolicy(sizePolicy1)
        self.label_Limit.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.label_Limit)

        self.lineEdit_Limit = QLineEdit(self.groupBox_control)
        self.lineEdit_Limit.setObjectName(u"lineEdit_Limit")
        sizePolicy1.setHeightForWidth(self.lineEdit_Limit.sizePolicy().hasHeightForWidth())
        self.lineEdit_Limit.setSizePolicy(sizePolicy1)
        self.lineEdit_Limit.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedLimit.addWidget(self.lineEdit_Limit)

        self.label_LimitUnits = QLabel(self.groupBox_control)
        self.label_LimitUnits.setObjectName(u"label_LimitUnits")

        self.HBoxLayout_pulsedLimit.addWidget(self.label_LimitUnits)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedLimit)

        self.HBoxLayout_pulsedNPLC = QHBoxLayout()
        self.HBoxLayout_pulsedNPLC.setObjectName(u"HBoxLayout_pulsedNPLC")
        self.label_NPLC = QLabel(self.groupBox_control)
        self.label_NPLC.setObjectName(u"label_NPLC")
        sizePolicy1.setHeightForWidth(self.label_NPLC.sizePolicy().hasHeightForWidth())
        self.label_NPLC.setSizePolicy(sizePolicy1)
        self.label_NPLC.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_NPLC)

        self.lineEdit_NPLC = QLineEdit(self.groupBox_control)
        self.lineEdit_NPLC.setObjectName(u"lineEdit_NPLC")
        sizePolicy1.setHeightForWidth(self.lineEdit_NPLC.sizePolicy().hasHeightForWidth())
        self.lineEdit_NPLC.setSizePolicy(sizePolicy1)
        self.lineEdit_NPLC.setMinimumSize(QSize(20, 0))
        self.lineEdit_NPLC.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedNPLC.addWidget(self.lineEdit_NPLC)

        self.label_NPLCUnits = QLabel(self.groupBox_control)
        self.label_NPLCUnits.setObjectName(u"label_NPLCUnits")

        self.HBoxLayout_pulsedNPLC.addWidget(self.label_NPLCUnits)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedNPLC)

        self.HBoxLayout_pulsedPause = QHBoxLayout()
        self.HBoxLayout_pulsedPause.setObjectName(u"HBoxLayout_pulsedPause")
        self.label_pulsedPause_2 = QLabel(self.groupBox_control)
        self.label_pulsedPause_2.setObjectName(u"label_pulsedPause_2")
        sizePolicy1.setHeightForWidth(self.label_pulsedPause_2.sizePolicy().hasHeightForWidth())
        self.label_pulsedPause_2.setSizePolicy(sizePolicy1)
        self.label_pulsedPause_2.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause_2)

        self.lineEdit_Pause = QLineEdit(self.groupBox_control)
        self.lineEdit_Pause.setObjectName(u"lineEdit_Pause")
        sizePolicy1.setHeightForWidth(self.lineEdit_Pause.sizePolicy().hasHeightForWidth())
        self.lineEdit_Pause.setSizePolicy(sizePolicy1)
        self.lineEdit_Pause.setMinimumSize(QSize(20, 0))
        self.lineEdit_Pause.setBaseSize(QSize(0, 0))

        self.HBoxLayout_pulsedPause.addWidget(self.lineEdit_Pause)

        self.label_pulsedPause = QLabel(self.groupBox_control)
        self.label_pulsedPause.setObjectName(u"label_pulsedPause")

        self.HBoxLayout_pulsedPause.addWidget(self.label_pulsedPause)


        self.HBoxLayout_pulsedLine1.addLayout(self.HBoxLayout_pulsedPause)

        self.HBoxLayout_pulsedLine1.setStretch(1, 10)
        self.HBoxLayout_pulsedLine1.setStretch(2, 10)
        self.HBoxLayout_pulsedLine1.setStretch(3, 10)
        self.HBoxLayout_pulsedLine1.setStretch(4, 10)
        self.HBoxLayout_pulsedLine1.setStretch(5, 10)

        self.verticalLayout_9.addLayout(self.HBoxLayout_pulsedLine1)

        self.HBoxLayout_pulsedLine2 = QHBoxLayout()
        self.HBoxLayout_pulsedLine2.setObjectName(u"HBoxLayout_pulsedLine2")
        self.HBoxLayout_pulsedDelayMode = QHBoxLayout()
        self.HBoxLayout_pulsedDelayMode.setObjectName(u"HBoxLayout_pulsedDelayMode")
        self.label_pulsedDelayMode = QLabel(self.groupBox_control)
        self.label_pulsedDelayMode.setObjectName(u"label_pulsedDelayMode")
        sizePolicy1.setHeightForWidth(self.label_pulsedDelayMode.sizePolicy().hasHeightForWidth())
        self.label_pulsedDelayMode.setSizePolicy(sizePolicy1)
        self.label_pulsedDelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.label_pulsedDelayMode)

        self.comboBox_DelayMode = QComboBox(self.groupBox_control)
        self.comboBox_DelayMode.addItem("")
        self.comboBox_DelayMode.addItem("")
        self.comboBox_DelayMode.setObjectName(u"comboBox_DelayMode")
        sizePolicy1.setHeightForWidth(self.comboBox_DelayMode.sizePolicy().hasHeightForWidth())
        self.comboBox_DelayMode.setSizePolicy(sizePolicy1)
        self.comboBox_DelayMode.setMinimumSize(QSize(80, 0))

        self.HBoxLayout_pulsedDelayMode.addWidget(self.comboBox_DelayMode)


        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelayMode)

        self.HBoxLayout_pulsedDelay = QHBoxLayout()
        self.HBoxLayout_pulsedDelay.setObjectName(u"HBoxLayout_pulsedDelay")
        self.label_Delay = QLabel(self.groupBox_control)
        self.label_Delay.setObjectName(u"label_Delay")
        sizePolicy1.setHeightForWidth(self.label_Delay.sizePolicy().hasHeightForWidth())
        self.label_Delay.setSizePolicy(sizePolicy1)
        self.label_Delay.setMinimumSize(QSize(40, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.label_Delay)

        self.lineEdit_Delay = QLineEdit(self.groupBox_control)
        self.lineEdit_Delay.setObjectName(u"lineEdit_Delay")
        sizePolicy1.setHeightForWidth(self.lineEdit_Delay.sizePolicy().hasHeightForWidth())
        self.lineEdit_Delay.setSizePolicy(sizePolicy1)
        self.lineEdit_Delay.setMinimumSize(QSize(20, 0))

        self.HBoxLayout_pulsedDelay.addWidget(self.lineEdit_Delay)

        self.label_DelayUnits = QLabel(self.groupBox_control)
        self.label_DelayUnits.setObjectName(u"label_DelayUnits")

        self.HBoxLayout_pulsedDelay.addWidget(self.label_DelayUnits)


        self.HBoxLayout_pulsedLine2.addLayout(self.HBoxLayout_pulsedDelay)

        self.HBoxLayout_pulsedLine2.setStretch(0, 10)
        self.HBoxLayout_pulsedLine2.setStretch(1, 10)

        self.verticalLayout_9.addLayout(self.HBoxLayout_pulsedLine2)


        self.verticalLayout.addWidget(self.groupBox_control)

        self.groupBox = QGroupBox(self.groupBox_general)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.spectro_check_after = QCheckBox(self.groupBox)
        self.spectro_check_after.setObjectName(u"spectro_check_after")

        self.horizontalLayout_2.addWidget(self.spectro_check_after)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.spectro_pause = QCheckBox(self.groupBox)
        self.spectro_pause.setObjectName(u"spectro_pause")

        self.horizontalLayout.addWidget(self.spectro_pause)

        self.spectro_pause_time = QDoubleSpinBox(self.groupBox)
        self.spectro_pause_time.setObjectName(u"spectro_pause_time")
        self.spectro_pause_time.setMaximum(15.000000000000000)
        self.spectro_pause_time.setSingleStep(0.500000000000000)

        self.horizontalLayout.addWidget(self.spectro_pause_time)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.spectro_use_last_integ = QCheckBox(self.groupBox)
        self.spectro_use_last_integ.setObjectName(u"spectro_use_last_integ")

        self.horizontalLayout_2.addWidget(self.spectro_use_last_integ)


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
        Form.setWindowTitle(QCoreApplication.translate("Form", u"SpecSMU_settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", u"SMU settings", None))
        self.groupBox_dependency.setTitle(QCoreApplication.translate("Form", u"Dependencies", None))
        self.label.setText(QCoreApplication.translate("Form", u"SMU Plugin", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Spectrometer Plugin", None))
        self.groupBox_general_2.setTitle(QCoreApplication.translate("Form", u"General", None))
        self.label_Channel.setText(QCoreApplication.translate("Form", u"Source channel", None))
        self.comboBox_channel.setItemText(0, QCoreApplication.translate("Form", u"smuA", None))
        self.comboBox_channel.setItemText(1, QCoreApplication.translate("Form", u"smuB", None))

        self.label_inject.setText(QCoreApplication.translate("Form", u"Inject", None))
        self.comboBox_inject.setItemText(0, QCoreApplication.translate("Form", u"Current", None))
        self.comboBox_inject.setItemText(1, QCoreApplication.translate("Form", u"Voltage", None))

        self.label_mode.setText(QCoreApplication.translate("Form", u"Mode", None))
        self.comboBox_mode.setItemText(0, QCoreApplication.translate("Form", u"Continuous", None))
        self.comboBox_mode.setItemText(1, QCoreApplication.translate("Form", u"Pulsed", None))
        self.comboBox_mode.setItemText(2, QCoreApplication.translate("Form", u"Mixed", None))

        self.label_sourceSenseMode.setText(QCoreApplication.translate("Form", u"Sense", None))
        self.comboBox_sourceSenseMode.setItemText(0, QCoreApplication.translate("Form", u"2 wire", None))
        self.comboBox_sourceSenseMode.setItemText(1, QCoreApplication.translate("Form", u"4 wire", None))
        self.comboBox_sourceSenseMode.setItemText(2, QCoreApplication.translate("Form", u"2 & 4 wire", None))

        self.checkBox_singleChannel.setText(QCoreApplication.translate("Form", u"Use single channel", None))
        self.groupBox_control.setTitle(QCoreApplication.translate("Form", u"Control", None))
        self.label_Start.setText(QCoreApplication.translate("Form", u"Start", None))
        self.lineEdit_Start.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_StartUnits.setText(QCoreApplication.translate("Form", u"A", None))
        self.label_End.setText(QCoreApplication.translate("Form", u"End", None))
        self.lineEdit_End.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_EndUnits.setText(QCoreApplication.translate("Form", u"A", None))
        self.label_Points.setText(QCoreApplication.translate("Form", u"Points", None))
        self.lineEdit_Points.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_Limit.setText(QCoreApplication.translate("Form", u"Limit", None))
        self.lineEdit_Limit.setText(QCoreApplication.translate("Form", u"0", None))
        self.label_LimitUnits.setText(QCoreApplication.translate("Form", u"V", None))
        self.label_NPLC.setText(QCoreApplication.translate("Form", u"NPLC", None))
        self.lineEdit_NPLC.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_NPLCUnits.setText(QCoreApplication.translate("Form", u"ms", None))
        self.label_pulsedPause_2.setText(QCoreApplication.translate("Form", u"Pause", None))
        self.lineEdit_Pause.setText(QCoreApplication.translate("Form", u"1", None))
        self.label_pulsedPause.setText(QCoreApplication.translate("Form", u"s", None))
        self.label_pulsedDelayMode.setText(QCoreApplication.translate("Form", u"Delay mode", None))
        self.comboBox_DelayMode.setItemText(0, QCoreApplication.translate("Form", u"Auto", None))
        self.comboBox_DelayMode.setItemText(1, QCoreApplication.translate("Form", u"Manual", None))

        self.label_Delay.setText(QCoreApplication.translate("Form", u"Delay", None))
        self.lineEdit_Delay.setText(QCoreApplication.translate("Form", u"10", None))
        self.label_DelayUnits.setText(QCoreApplication.translate("Form", u"ms", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Spectrometer", None))
        self.spectro_check_after.setText(QCoreApplication.translate("Form", u"Measure IV before and after", None))
        self.spectro_pause.setText(QCoreApplication.translate("Form", u"pause", None))
        self.spectro_use_last_integ.setText(QCoreApplication.translate("Form", u"getAutoTime initial guess from last integration time", None))
    # retranslateUi

