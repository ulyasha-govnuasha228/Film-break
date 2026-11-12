from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setStyleSheet("\n"
"QPushButton {\n"
"    background-color: rgba(180, 160, 210, 90);\n"
"    background-image: none;\n"
"    border-image: none;\n"
"    color: rgb(245, 240, 255);\n"
"    border: 1px solid rgba(220, 205, 255, 150);\n"
"    border-radius: 8px;\n"
"    padding: 6px 12px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(180, 160, 210, 140);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgba(140, 120, 175, 180);\n"
"}\n"
"\n"
"")
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.scrollArea = QtWidgets.QScrollArea(parent=Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 376, 239))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "+"))
