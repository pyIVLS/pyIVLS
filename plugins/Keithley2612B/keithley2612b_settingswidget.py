################################################################################
## Form generated from reading UI file 'Keithley2612B_settingsWidget.ui'
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
        Form.resize(787, 494)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, -66, 753, 540))
        self.verticalLayout_10 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.groupBox_HWsettings = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_HWsettings.setObjectName("groupBox_HWsettings")
        self.groupBox_HWsettings.setMinimumSize(QSize(0, 0))
        self.groupBox_HWsettings.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_HWsettings)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.HBoxLayout_sourceChannel_4 = QHBoxLayout()
        self.HBoxLayout_sourceChannel_4.setObjectName("HBoxLayout_sourceChannel_4")
        self.HBoxLayout_sourceHighC_4 = QHBoxLayout()
        self.HBoxLayout_sourceHighC_4.setObjectName("HBoxLayout_sourceHighC_4")
        self.labelAddress = QLabel(self.groupBox_HWsettings)
        self.labelAddress.setObjectName("labelAddress")

        self.HBoxLayout_sourceHighC_4.addWidget(self.labelAddress)

        self.lineEditAddress = QLineEdit(self.groupBox_HWsettings)
        self.lineEditAddress.setObjectName("lineEditAddress")

        self.HBoxLayout_sourceHighC_4.addWidget(self.lineEditAddress)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceHighC_4.addItem(self.horizontalSpacer)

        self.HBoxLayout_sourceChannel_4.addLayout(self.HBoxLayout_sourceHighC_4)

        self.verticalLayout_2.addLayout(self.HBoxLayout_sourceChannel_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self.groupBox_HWsettings)
        self.label.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEditETH = QLineEdit(self.groupBox_HWsettings)
        self.lineEditETH.setObjectName("lineEditETH")

        self.horizontalLayout.addWidget(self.lineEditETH)

        self.label_3 = QLabel(self.groupBox_HWsettings)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.lineEditPort = QLineEdit(self.groupBox_HWsettings)
        self.lineEditPort.setObjectName("lineEditPort")

        self.horizontalLayout.addWidget(self.lineEditPort)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QLabel(self.groupBox_HWsettings)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.backendCombobox = QComboBox(self.groupBox_HWsettings)
        self.backendCombobox.addItem("")
        self.backendCombobox.addItem("")
        self.backendCombobox.addItem("")
        self.backendCombobox.setObjectName("backendCombobox")

        self.horizontalLayout_2.addWidget(self.backendCombobox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_10.addWidget(self.groupBox_HWsettings)

        self.groupBox_channels = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_channels.setObjectName("groupBox_channels")
        self.groupBox_channels.setMinimumSize(QSize(0, 0))
        self.groupBox_channels.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_channels)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox_source = QGroupBox(self.groupBox_channels)
        self.groupBox_source.setObjectName("groupBox_source")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_source)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.HBoxLayout_sourceChannel = QHBoxLayout()
        self.HBoxLayout_sourceChannel.setObjectName("HBoxLayout_sourceChannel")
        self.HBoxLayout_sourceHighC = QHBoxLayout()
        self.HBoxLayout_sourceHighC.setObjectName("HBoxLayout_sourceHighC")
        self.checkBox_sourceHighC = QCheckBox(self.groupBox_source)
        self.checkBox_sourceHighC.setObjectName("checkBox_sourceHighC")

        self.HBoxLayout_sourceHighC.addWidget(self.checkBox_sourceHighC)

        self.HBoxLayout_sourceChannel.addLayout(self.HBoxLayout_sourceHighC)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceChannel.addItem(self.horizontalSpacer_20)

        self.HBoxLayout_sourceChannel.setStretch(0, 10)
        self.HBoxLayout_sourceChannel.setStretch(1, 40)

        self.verticalLayout_8.addLayout(self.HBoxLayout_sourceChannel)

        self.HBoxLayout_sourceFilter = QHBoxLayout()
        self.HBoxLayout_sourceFilter.setObjectName("HBoxLayout_sourceFilter")
        self.label_sourceFilter = QLabel(self.groupBox_source)
        self.label_sourceFilter.setObjectName("label_sourceFilter")

        self.HBoxLayout_sourceFilter.addWidget(self.label_sourceFilter)

        self.comboBox_sourceFilter = QComboBox(self.groupBox_source)
        self.comboBox_sourceFilter.addItem("")
        self.comboBox_sourceFilter.addItem("")
        self.comboBox_sourceFilter.setObjectName("comboBox_sourceFilter")

        self.HBoxLayout_sourceFilter.addWidget(self.comboBox_sourceFilter)

        self.lineEdit_sourceFilter = QLineEdit(self.groupBox_source)
        self.lineEdit_sourceFilter.setObjectName("lineEdit_sourceFilter")
        self.lineEdit_sourceFilter.setEnabled(False)

        self.HBoxLayout_sourceFilter.addWidget(self.lineEdit_sourceFilter)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_sourceFilter.addItem(self.horizontalSpacer_4)

        self.HBoxLayout_sourceFilter.setStretch(0, 1)
        self.HBoxLayout_sourceFilter.setStretch(1, 1)
        self.HBoxLayout_sourceFilter.setStretch(2, 1)
        self.HBoxLayout_sourceFilter.setStretch(3, 2)

        self.verticalLayout_8.addLayout(self.HBoxLayout_sourceFilter)

        self.HBoxLayout_delayFactor = QHBoxLayout()
        self.HBoxLayout_delayFactor.setObjectName("HBoxLayout_delayFactor")
        self.label_sourceDelayFactor = QLabel(self.groupBox_source)
        self.label_sourceDelayFactor.setObjectName("label_sourceDelayFactor")

        self.HBoxLayout_delayFactor.addWidget(self.label_sourceDelayFactor)

        self.lineEdit_sourceDelayFactor = QLineEdit(self.groupBox_source)
        self.lineEdit_sourceDelayFactor.setObjectName("lineEdit_sourceDelayFactor")

        self.HBoxLayout_delayFactor.addWidget(self.lineEdit_sourceDelayFactor)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_delayFactor.addItem(self.horizontalSpacer_7)

        self.HBoxLayout_delayFactor.setStretch(0, 1)
        self.HBoxLayout_delayFactor.setStretch(1, 1)
        self.HBoxLayout_delayFactor.setStretch(2, 3)

        self.verticalLayout_8.addLayout(self.HBoxLayout_delayFactor)

        self.verticalLayout_6.addWidget(self.groupBox_source)

        self.groupBox_drain = QGroupBox(self.groupBox_channels)
        self.groupBox_drain.setObjectName("groupBox_drain")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_drain)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.HBoxLayout_drainChannel = QHBoxLayout()
        self.HBoxLayout_drainChannel.setObjectName("HBoxLayout_drainChannel")
        self.HBoxLayout_drainHighC = QHBoxLayout()
        self.HBoxLayout_drainHighC.setObjectName("HBoxLayout_drainHighC")
        self.checkBox_drainHighC = QCheckBox(self.groupBox_drain)
        self.checkBox_drainHighC.setObjectName("checkBox_drainHighC")

        self.HBoxLayout_drainHighC.addWidget(self.checkBox_drainHighC)

        self.HBoxLayout_drainChannel.addLayout(self.HBoxLayout_drainHighC)

        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainChannel.addItem(self.horizontalSpacer_23)

        self.HBoxLayout_drainChannel.setStretch(0, 10)
        self.HBoxLayout_drainChannel.setStretch(1, 40)

        self.verticalLayout_7.addLayout(self.HBoxLayout_drainChannel)

        self.HBoxLayout_drainFilter = QHBoxLayout()
        self.HBoxLayout_drainFilter.setObjectName("HBoxLayout_drainFilter")
        self.label_drainFilter = QLabel(self.groupBox_drain)
        self.label_drainFilter.setObjectName("label_drainFilter")

        self.HBoxLayout_drainFilter.addWidget(self.label_drainFilter)

        self.comboBox_drainFilter = QComboBox(self.groupBox_drain)
        self.comboBox_drainFilter.addItem("")
        self.comboBox_drainFilter.addItem("")
        self.comboBox_drainFilter.setObjectName("comboBox_drainFilter")

        self.HBoxLayout_drainFilter.addWidget(self.comboBox_drainFilter)

        self.lineEdit_drainFilter = QLineEdit(self.groupBox_drain)
        self.lineEdit_drainFilter.setObjectName("lineEdit_drainFilter")
        self.lineEdit_drainFilter.setEnabled(False)

        self.HBoxLayout_drainFilter.addWidget(self.lineEdit_drainFilter)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainFilter.addItem(self.horizontalSpacer_5)

        self.HBoxLayout_drainFilter.setStretch(0, 1)
        self.HBoxLayout_drainFilter.setStretch(1, 1)
        self.HBoxLayout_drainFilter.setStretch(2, 1)
        self.HBoxLayout_drainFilter.setStretch(3, 2)

        self.verticalLayout_7.addLayout(self.HBoxLayout_drainFilter)

        self.HBoxLayout_drainDelayFactor = QHBoxLayout()
        self.HBoxLayout_drainDelayFactor.setObjectName("HBoxLayout_drainDelayFactor")
        self.label_drainDelayFactor = QLabel(self.groupBox_drain)
        self.label_drainDelayFactor.setObjectName("label_drainDelayFactor")

        self.HBoxLayout_drainDelayFactor.addWidget(self.label_drainDelayFactor)

        self.lineEdit_drainDelayFactor = QLineEdit(self.groupBox_drain)
        self.lineEdit_drainDelayFactor.setObjectName("lineEdit_drainDelayFactor")

        self.HBoxLayout_drainDelayFactor.addWidget(self.lineEdit_drainDelayFactor)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_drainDelayFactor.addItem(self.horizontalSpacer_8)

        self.HBoxLayout_drainDelayFactor.setStretch(0, 1)
        self.HBoxLayout_drainDelayFactor.setStretch(1, 1)
        self.HBoxLayout_drainDelayFactor.setStretch(2, 3)

        self.verticalLayout_7.addLayout(self.HBoxLayout_drainDelayFactor)

        self.verticalLayout_6.addWidget(self.groupBox_drain)

        self.verticalLayout_10.addWidget(self.groupBox_channels)

        self.HBoxLayout_Initialize = QHBoxLayout()
        self.HBoxLayout_Initialize.setObjectName("HBoxLayout_Initialize")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.HBoxLayout_Initialize.addItem(self.horizontalSpacer_6)

        self.button_Init = QPushButton(self.scrollAreaWidgetContents)
        self.button_Init.setObjectName("button_Init")

        self.HBoxLayout_Initialize.addWidget(self.button_Init)

        self.verticalLayout_10.addLayout(self.HBoxLayout_Initialize)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Keithley 2512B settings", None))
        self.groupBox_HWsettings.setTitle(QCoreApplication.translate("Form", "Hardware", None))
        self.labelAddress.setText(QCoreApplication.translate("Form", "USB Address", None))
        self.label.setText(QCoreApplication.translate("Form", "ETH Address", None))
        self.label_3.setText(QCoreApplication.translate("Form", "ETH port", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Backend", None))
        self.backendCombobox.setItemText(0, QCoreApplication.translate("Form", "USB", None))
        self.backendCombobox.setItemText(1, QCoreApplication.translate("Form", "Ethernet", None))
        self.backendCombobox.setItemText(2, QCoreApplication.translate("Form", "MOCK", None))

        self.groupBox_channels.setTitle(QCoreApplication.translate("Form", "Channels", None))
        self.groupBox_source.setTitle(QCoreApplication.translate("Form", "Source", None))
        self.checkBox_sourceHighC.setText(QCoreApplication.translate("Form", "High C mode", None))
        self.label_sourceFilter.setText(QCoreApplication.translate("Form", "Filter", None))
        self.comboBox_sourceFilter.setItemText(0, QCoreApplication.translate("Form", "Off", None))
        self.comboBox_sourceFilter.setItemText(1, QCoreApplication.translate("Form", "Repeat average", None))

        self.lineEdit_sourceFilter.setText(QCoreApplication.translate("Form", "1", None))
        self.label_sourceDelayFactor.setText(QCoreApplication.translate("Form", "Delay factor", None))
        self.lineEdit_sourceDelayFactor.setText(QCoreApplication.translate("Form", "1", None))
        self.groupBox_drain.setTitle(QCoreApplication.translate("Form", "Drain", None))
        self.checkBox_drainHighC.setText(QCoreApplication.translate("Form", "High C mode", None))
        self.label_drainFilter.setText(QCoreApplication.translate("Form", "Filter", None))
        self.comboBox_drainFilter.setItemText(0, QCoreApplication.translate("Form", "Off", None))
        self.comboBox_drainFilter.setItemText(1, QCoreApplication.translate("Form", "Repeat average", None))

        self.lineEdit_drainFilter.setText(QCoreApplication.translate("Form", "1", None))
        self.label_drainDelayFactor.setText(QCoreApplication.translate("Form", "Delay factor", None))
        self.lineEdit_drainDelayFactor.setText(QCoreApplication.translate("Form", "1", None))
        self.button_Init.setText(QCoreApplication.translate("Form", "Reset", None))

    # retranslateUi
