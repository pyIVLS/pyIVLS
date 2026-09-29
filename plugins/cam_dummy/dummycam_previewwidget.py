################################################################################
## Form generated from reading UI file 'dummycam_previewWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import QLabel, QVBoxLayout


class Ui_previewForm:
    def setupUi(self, previewForm):
        if not previewForm.objectName():
            previewForm.setObjectName("previewForm")
        previewForm.resize(594, 474)
        previewForm.setMinimumSize(QSize(200, 200))
        self.verticalLayout = QVBoxLayout(previewForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.previewLabel = QLabel(previewForm)
        self.previewLabel.setObjectName("previewLabel")

        self.verticalLayout.addWidget(self.previewLabel)

        self.retranslateUi(previewForm)

        QMetaObject.connectSlotsByName(previewForm)

    # setupUi

    def retranslateUi(self, previewForm):
        previewForm.setWindowTitle(QCoreApplication.translate("previewForm", "Camera preview", None))
        self.previewLabel.setText("")

    # retranslateUi
