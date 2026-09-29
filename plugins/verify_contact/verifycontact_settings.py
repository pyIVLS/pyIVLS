################################################################################
## Form generated from reading UI file 'verifyContact_Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1055, 895)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1035, 875))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.touchDetBox = QComboBox(self.scrollAreaWidgetContents)
        self.touchDetBox.setObjectName("touchDetBox")

        self.gridLayout_3.addWidget(self.touchDetBox, 4, 0, 1, 1)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName("label")
        self.label.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton.setObjectName("pushButton")

        self.gridLayout_3.addWidget(self.pushButton, 6, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 7, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "touchDetect settings", None))
        self.touchDetBox.setPlaceholderText(QCoreApplication.translate("Form", "No touch detect plugins found", None))
        self.label.setText(QCoreApplication.translate("Form", "Touch detection plugin", None))
        self.pushButton.setText(QCoreApplication.translate("Form", "Verify contact", None))

    # retranslateUi
