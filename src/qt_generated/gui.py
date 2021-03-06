# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_ui/qt-gui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(776, 812)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.button_Parse = QtWidgets.QPushButton(self.tab)
        self.button_Parse.setObjectName("button_Parse")
        self.gridLayout.addWidget(self.button_Parse, 0, 0, 1, 1)
        self.cb_Parser = QtWidgets.QComboBox(self.tab)
        self.cb_Parser.setObjectName("cb_Parser")
        self.gridLayout.addWidget(self.cb_Parser, 0, 1, 1, 1)
        self.button_StopParsing = QtWidgets.QPushButton(self.tab)
        self.button_StopParsing.setEnabled(False)
        self.button_StopParsing.setObjectName("button_StopParsing")
        self.gridLayout.addWidget(self.button_StopParsing, 1, 0, 1, 1)
        self.checkBox_ConvertLF = QtWidgets.QCheckBox(self.tab)
        self.checkBox_ConvertLF.setChecked(True)
        self.checkBox_ConvertLF.setObjectName("checkBox_ConvertLF")
        self.gridLayout.addWidget(self.checkBox_ConvertLF, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textEdit_input = QtWidgets.QPlainTextEdit(self.tab)
        self.textEdit_input.setObjectName("textEdit_input")
        self.horizontalLayout.addWidget(self.textEdit_input)
        self.treeWidget = QtWidgets.QTreeWidget(self.tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(200)
        self.horizontalLayout.addWidget(self.treeWidget)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 8, 0, 1, 1)
        self.tableView_Sessions = QtWidgets.QTableView(self.tab_2)
        self.tableView_Sessions.setObjectName("tableView_Sessions")
        self.gridLayout_2.addWidget(self.tableView_Sessions, 9, 0, 1, 3)
        self.lineEdit_LocalBindAddress = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_LocalBindAddress.setObjectName("lineEdit_LocalBindAddress")
        self.gridLayout_2.addWidget(self.lineEdit_LocalBindAddress, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.lineEdit_ServerConnectionString = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_ServerConnectionString.setObjectName("lineEdit_ServerConnectionString")
        self.gridLayout_2.addWidget(self.lineEdit_ServerConnectionString, 3, 0, 1, 1)
        self.button_StartProxy = QtWidgets.QPushButton(self.tab_2)
        self.button_StartProxy.setEnabled(False)
        self.button_StartProxy.setObjectName("button_StartProxy")
        self.gridLayout_2.addWidget(self.button_StartProxy, 2, 2, 1, 1)
        self.button_StopProxy = QtWidgets.QPushButton(self.tab_2)
        self.button_StopProxy.setEnabled(False)
        self.button_StopProxy.setObjectName("button_StopProxy")
        self.gridLayout_2.addWidget(self.button_StopProxy, 3, 2, 1, 1)
        self.button_testProxyConfig = QtWidgets.QPushButton(self.tab_2)
        self.button_testProxyConfig.setObjectName("button_testProxyConfig")
        self.gridLayout_2.addWidget(self.button_testProxyConfig, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.cb_interception = QtWidgets.QCheckBox(self.tab_2)
        self.cb_interception.setObjectName("cb_interception")
        self.gridLayout_2.addWidget(self.cb_interception, 0, 2, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 776, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actiontest = QtWidgets.QAction(MainWindow)
        self.actiontest.setObjectName("actiontest")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_Parse.setText(_translate("MainWindow", "Parse"))
        self.button_StopParsing.setText(_translate("MainWindow", "Stop parsing"))
        self.checkBox_ConvertLF.setText(_translate("MainWindow", "Convert \"\\n\" to \"\\r\\n\""))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Rule"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Parser"))
        self.label_2.setText(_translate("MainWindow", "Connections"))
        self.lineEdit_LocalBindAddress.setText(_translate("MainWindow", "127.0.0.1:10143"))
        self.label_3.setText(_translate("MainWindow", "Local listening address (e. g. 127.0.0.1:10143)"))
        self.lineEdit_ServerConnectionString.setText(_translate("MainWindow", "127.0.0.1:143"))
        self.button_StartProxy.setText(_translate("MainWindow", "Start Proxy"))
        self.button_StopProxy.setText(_translate("MainWindow", "Stop Proxy"))
        self.button_testProxyConfig.setText(_translate("MainWindow", "Test Proxy Configuration"))
        self.label.setText(_translate("MainWindow", "Server Address (e.g. 127.0.0.1:143)"))
        self.cb_interception.setText(_translate("MainWindow", "Intercept New Connections"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Proxy"))
        self.actiontest.setText(_translate("MainWindow", "test"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
