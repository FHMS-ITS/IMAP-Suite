from qt_generated.gui import Ui_MainWindow
from qt_implementation.qt_pendingMessage import AppPendingDialog
from qt_implementation.qt_imapSession import AppSessionWindow
from qt_utils.qt_QThreads import StopProxyThread,  TestProxyConfigThread, ParserThread, ProxyThread
from qt_utils.qt_ViewModels import ImapSessionListModel
from imap.Imap4rev1Parser import Imap4Rev1Parser
from qt_utils.qt_utils import larkTreeToQtTreeWidgetItem
from utils.imap_constants import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QHeaderView, QTableView, QTreeWidgetItem, QMessageBox, QApplication, QMainWindow

import sys


class AppWindow(Ui_MainWindow):
    def __init__(self, mainWindow):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.parsingThread = None
        self.proxyThread = None
        self.stopProxyThread = None
        self.startingRules = PARSING_STARTING_RULES
        self.sessionListModel = ImapSessionListModel()

        self.ui.setupUi(mainWindow)
        mainWindow.show()

        self.ui.button_Parse.clicked.connect(self.button_Parse_click)
        self.ui.button_testProxyConfig.clicked.connect(self.button_submitServerConnection_click)
        self.ui.button_StartProxy.clicked.connect(self.button_proxyStart_click)
        self.ui.button_StopProxy.clicked.connect(self.button_proxyStop_click)

        self.ui.cb_Parser.addItems(self.startingRules)

        self.ui.tmpSplitter = QSplitter(Qt.Horizontal)

        self.ui.tmpSplitter.addWidget(self.ui.textEdit_input)
        self.ui.tmpSplitter.addWidget(self.ui.treeWidget)
        self.ui.tmpSplitter.setSizes([50,50])

        self.ui.horizontalLayout.addWidget(self.ui.tmpSplitter)

        self.ui.tableView_Sessions.setModel(self.sessionListModel)
        self.ui.tableView_Sessions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_Sessions.setSelectionBehavior(QTableView.SelectRows)
        self.ui.tableView_Sessions.setSelectionMode(QTableView.SingleSelection)

        self.ui.tableView_Sessions.doubleClicked.connect(self.tableView_doubleClicked_Item)

        self.ui.lineEdit_ServerConnectionString.textChanged.connect(self.lineEdit_TextChanged)
        self.ui.lineEdit_LocalBindAddress.textChanged.connect(self.lineEdit_TextChanged)

        self.ui.cb_interception.stateChanged.connect(self.cb_interception_changed)

        self.childWindows = dict()
        self.tmpWindows = []

    def lineEdit_TextChanged(self, text):
        self.ui.button_StartProxy.setEnabled(False)

    def cb_interception_changed(self, state):
        if self.proxyThread:
            self.proxyThread.intercepted = self.ui.cb_interception.isChecked()

    def tableView_doubleClicked_Item(self, index):
        row = index.row()
        if row in self.childWindows:
            w = self.childWindows[row]
            w.raise_()
            w.activateWindow()
        else:
            w = AppSessionWindow(row, self.sessionListModel.getItem(index), self.proxyThread)
            if self.proxyThread:
                self.proxyThread.sigSessionHistoryChanged.connect(w.proxyThreadSignalUpdateHistoryTable)
            self.childWindows[row] = w
            w.sigClose.connect(self.imapSessionWindowSignalClose)
            w.show()


    def imapSessionWindowSignalClose(self, row):
        del self.childWindows[row]

    def proxyThreadSignalNewSession(self):
        self.sessionListModel.layoutChanged.emit()

    def proxyThreadSignalUpdateTable(self):
        self.sessionListModel.layoutChanged.emit()

    def proxyThreadSignalInterception(self, session):
        w = AppPendingDialog(session)
        self.tmpWindows.append(w)
        w.show()

    def parsingThreadParsingDone(self):
        treeList, rest = self.parsingThread.result

        self.ui.treeWidget.clear()
        for tree in treeList:
            self.ui.treeWidget.addTopLevelItem(larkTreeToQtTreeWidgetItem(tree))

        if rest != '':
            treeRest = QTreeWidgetItem()
            treeRest.setText(0, QTREE_REST)
            treeRest.setText(1, rest)
            self.ui.treeWidget.addTopLevelItem(treeRest)
        self.ui.treeWidget.setColumnWidth(0, 250)
        self.ui.treeWidget.expandAll()

        self.parsingThread = None

        self.ui.button_Parse.setEnabled(True)
        self.ui.button_StopParsing.setEnabled(False)

    def parsingThreadTerminate(self):
        self.parsingThread.terminate()
        self.parsingThread = None
        self.ui.button_Parse.setEnabled(True)
        self.ui.button_StopParsing.setEnabled(False)

    def testProxyThreadError(self, string):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(string)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def testProxyThreadSuccess(self):
        if self.proxyThread is not None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Test successful. Restart Proxy...')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        else:
            self.ui.button_StartProxy.setEnabled(True)

    def button_proxyStart_click(self):
        self.ui.button_StartProxy.setEnabled(False)
        self.ui.button_StopProxy.setEnabled(True)
        self.ui.button_testProxyConfig.setEnabled(False)
        self.ui.lineEdit_LocalBindAddress.setEnabled(False)
        self.ui.lineEdit_ServerConnectionString.setEnabled(False)

        localAddress = self.ui.lineEdit_LocalBindAddress.text()
        serverAddress = self.ui.lineEdit_ServerConnectionString.text()
        intercepted = self.ui.cb_interception.isChecked()


        self.proxyThread = ProxyThread(self.sessionListModel, localAddress, serverAddress, intercepted)
        self.proxyThread.start()

        self.proxyThread.sigNewSession.connect(self.proxyThreadSignalNewSession)
        self.proxyThread.sigStateChanged.connect(self.proxyThreadSignalUpdateTable)
        self.proxyThread.sigInterception.connect(self.proxyThreadSignalInterception)

    def button_proxyStop_click(self):
        self.ui.button_StopProxy.setEnabled(False)
        self.proxyThread.abortThread = True
        self.stopProxyThread = StopProxyThread(self)
        self.stopProxyThread.start()

    def button_submitServerConnection_click(self):
        self.ui.button_StartProxy.setEnabled(False)
        localAddress = self.ui.lineEdit_LocalBindAddress.text()
        serverAddress = self.ui.lineEdit_ServerConnectionString.text()

        thread = TestProxyConfigThread(localAddress, serverAddress)
        thread.start()

        thread.sigTestProxyError.connect(self.testProxyThreadError)
        thread.sigTestProxySuccess.connect(self.testProxyThreadSuccess)

    def button_Parse_click(self):
        if self.parsingThread:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Still parsing...")
            msg.setWindowTitle("Parser busy")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        else:
            raw = self.ui.textEdit_input.toPlainText()
            startingRule = self.ui.cb_Parser.currentText()

            convertLFToCRLF = self.ui.checkBox_ConvertLF.isChecked()

            if convertLFToCRLF:
                raw = raw.replace('\n', '\r\n')

            self.parsingThread = ParserThread(raw, Imap4Rev1Parser(startingRule))

            self.parsingThread.sigParsingDone.connect(self.parsingThreadParsingDone)

            self.parsingThread.start()
            self.ui.button_StopParsing.setEnabled(True)
            self.ui.button_StopParsing.clicked.connect(self.parsingThreadTerminate)

            self.ui.button_Parse.setEnabled(False)

def trace_calls(frame, event, arg):
    if event != 'call':
        return
    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        # Ignore write() calls from print statements
        return
    func_line_no = frame.f_lineno
    func_filename = co.co_filename
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    print('Call to ' + str(func_name) + ' on line ' + str(func_line_no) + ' of ' + str(func_filename) + ' from line ' + str(caller_line_no) + ' of ' + str(caller_filename))
    return

def startGUI():
    #sys.settrace(trace_calls)

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    w = AppWindow(MainWindow)
    sys.exit(app.exec_())


