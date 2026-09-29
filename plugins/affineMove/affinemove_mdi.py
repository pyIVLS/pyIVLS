################################################################################
## Form generated from reading UI file 'affinemove_MDI.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import QGraphicsView, QVBoxLayout


class Ui_previewForm:
    def setupUi(self, previewForm):
        if not previewForm.objectName():
            previewForm.setObjectName("previewForm")
        previewForm.resize(600, 487)
        previewForm.setMinimumSize(QSize(200, 200))
        self.verticalLayout = QVBoxLayout(previewForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cameraview = QGraphicsView(previewForm)
        self.cameraview.setObjectName("cameraview")
        self.cameraview.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

        self.verticalLayout.addWidget(self.cameraview)

        self.retranslateUi(previewForm)

        QMetaObject.connectSlotsByName(previewForm)

    # setupUi

    def retranslateUi(self, previewForm):
        previewForm.setWindowTitle(QCoreApplication.translate("previewForm", "AffineMove preview", None))

    # retranslateUi
