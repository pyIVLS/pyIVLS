################################################################################
## Form generated from reading UI file 'pluginTemplate_MDIWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLabel


class Ui_previewForm:
    def setupUi(self, previewForm):
        if not previewForm.objectName():
            previewForm.setObjectName("previewForm")
        previewForm.resize(594, 474)
        previewForm.setMinimumSize(QSize(200, 200))
        self.gridLayout = QGridLayout(previewForm)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QLabel(previewForm)
        self.label.setObjectName("label")
        self.label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(previewForm)

        QMetaObject.connectSlotsByName(previewForm)

    # setupUi

    def retranslateUi(self, previewForm):
        previewForm.setWindowTitle(QCoreApplication.translate("previewForm", "Template MDI", None))
        self.label.setText(QCoreApplication.translate("previewForm", "Template MDI :)", None))

    # retranslateUi
