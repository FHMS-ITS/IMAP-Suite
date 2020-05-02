# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_ui/qt-pendingDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PendingDialog(object):
    def setupUi(self, PendingDialog):
        PendingDialog.setObjectName("PendingDialog")
        PendingDialog.resize(888, 725)
        PendingDialog.setSizeGripEnabled(True)
        PendingDialog.setModal(False)
        self.gridLayout_2 = QtWidgets.QGridLayout(PendingDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(PendingDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(PendingDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_ClientPeer = QtWidgets.QLineEdit(PendingDialog)
        self.lineEdit_ClientPeer.setEnabled(True)
        self.lineEdit_ClientPeer.setReadOnly(True)
        self.lineEdit_ClientPeer.setObjectName("lineEdit_ClientPeer")
        self.gridLayout.addWidget(self.lineEdit_ClientPeer, 1, 0, 1, 1)
        self.lineEdit_ServerPeer = QtWidgets.QLineEdit(PendingDialog)
        self.lineEdit_ServerPeer.setReadOnly(True)
        self.lineEdit_ServerPeer.setObjectName("lineEdit_ServerPeer")
        self.gridLayout.addWidget(self.lineEdit_ServerPeer, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(PendingDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.lineEdit_CurrentState = QtWidgets.QLineEdit(PendingDialog)
        self.lineEdit_CurrentState.setReadOnly(True)
        self.lineEdit_CurrentState.setObjectName("lineEdit_CurrentState")
        self.gridLayout.addWidget(self.lineEdit_CurrentState, 1, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)
        self.plainTextEdit_CommandRaw = QtWidgets.QPlainTextEdit(PendingDialog)
        self.plainTextEdit_CommandRaw.setObjectName("plainTextEdit_CommandRaw")
        self.gridLayout_2.addWidget(self.plainTextEdit_CommandRaw, 1, 0, 1, 1)
        self.treeWidget_CommandTree = QtWidgets.QTreeWidget(PendingDialog)
        self.treeWidget_CommandTree.setObjectName("treeWidget_CommandTree")
        self.gridLayout_2.addWidget(self.treeWidget_CommandTree, 1, 1, 1, 1)
        self.cb_Parser = QtWidgets.QComboBox(PendingDialog)
        self.cb_Parser.setObjectName("cb_Parser")
        self.gridLayout_2.addWidget(self.cb_Parser, 2, 0, 1, 1)
        self.button_Parse = QtWidgets.QPushButton(PendingDialog)
        self.button_Parse.setObjectName("button_Parse")
        self.gridLayout_2.addWidget(self.button_Parse, 2, 1, 1, 1)
        self.checkBox_ConvertLF = QtWidgets.QCheckBox(PendingDialog)
        self.checkBox_ConvertLF.setChecked(True)
        self.checkBox_ConvertLF.setObjectName("checkBox_ConvertLF")
        self.gridLayout_2.addWidget(self.checkBox_ConvertLF, 3, 0, 1, 1)
        self.button_Forward = QtWidgets.QPushButton(PendingDialog)
        self.button_Forward.setObjectName("button_Forward")
        self.gridLayout_2.addWidget(self.button_Forward, 3, 1, 1, 1)

        self.retranslateUi(PendingDialog)
        QtCore.QMetaObject.connectSlotsByName(PendingDialog)

    def retranslateUi(self, PendingDialog):
        _translate = QtCore.QCoreApplication.translate
        PendingDialog.setWindowTitle(_translate("PendingDialog", "Dialog"))
        self.label_2.setText(_translate("PendingDialog", "Server-Peer"))
        self.label.setText(_translate("PendingDialog", "Client-Peer"))
        self.label_3.setText(_translate("PendingDialog", "Current State"))
        self.treeWidget_CommandTree.headerItem().setText(0, _translate("PendingDialog", "Rule"))
        self.treeWidget_CommandTree.headerItem().setText(1, _translate("PendingDialog", "Data"))
        self.button_Parse.setText(_translate("PendingDialog", "Parse"))
        self.checkBox_ConvertLF.setText(_translate("PendingDialog", "Convert \"\\n\" to \"\\r\\n\""))
        self.button_Forward.setText(_translate("PendingDialog", "Forward"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PendingDialog = QtWidgets.QDialog()
    ui = Ui_PendingDialog()
    ui.setupUi(PendingDialog)
    PendingDialog.show()
    sys.exit(app.exec_())
