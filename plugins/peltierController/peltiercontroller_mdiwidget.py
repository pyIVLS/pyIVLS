################################################################################
## Form generated from reading UI file 'peltierController_MDIWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QTextEdit, QVBoxLayout


class Ui_previewForm:
    def setupUi(self, previewForm):
        if not previewForm.objectName():
            previewForm.setObjectName("previewForm")
        previewForm.resize(1027, 346)
        previewForm.setMinimumSize(QSize(400, 200))
        self.horizontalLayout = QHBoxLayout(previewForm)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.displayLayout = QVBoxLayout()
        self.displayLayout.setObjectName("displayLayout")

        self.horizontalLayout_2.addLayout(self.displayLayout)

        self.peltierOutputEdit = QTextEdit(previewForm)
        self.peltierOutputEdit.setObjectName("peltierOutputEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.peltierOutputEdit.sizePolicy().hasHeightForWidth())
        self.peltierOutputEdit.setSizePolicy(sizePolicy)
        self.peltierOutputEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.peltierOutputEdit)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(previewForm)

        QMetaObject.connectSlotsByName(previewForm)

    # setupUi

    def retranslateUi(self, previewForm):
        previewForm.setWindowTitle(QCoreApplication.translate("previewForm", "Temperature controller readout", None))

    # retranslateUi
