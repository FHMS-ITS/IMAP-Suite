from qt_generated.gui_imapSession import Ui_SessionDialog
from imap.ImapSession import ImapSession
from qt_utils.qt_QThreads import SendLocalCommandThread
from qt_utils.qt_utils import larkTreeToQtTreeWidgetItem

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QSplitter, QHeaderView, QTableView, QApplication

import sys

class AppSessionWindow(QDialog, Ui_SessionDialog):
    sigClose = pyqtSignal(int)

    def __init__(self, row, imapSession, qProxyThread):
        super(AppSessionWindow, self).__init__(None)

        self.setupUi(self)

        self.imapSession = imapSession
        self.qProxyThread = qProxyThread
        self.row = row
        self.currentTag = None

        #Tab 1
        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.tableView_SessionHistory)
        self.splitter1.addWidget(self.frame_CommandTuple)
        self.splitter1.setSizes([50, 50])
        self.tab.layout().addWidget(self.splitter1)

        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.tabWidget_Command)
        self.splitter2.addWidget(self.tabWidget_Response)
        self.splitter2.setSizes([50, 50])
        self.frame_CommandTuple.layout().addWidget(self.splitter2)

        self.lineEdit_ClientPeer.setText(str(self.imapSession.clientPeer))
        self.lineEdit_ServerPeer.setText(str(self.imapSession.serverPeer))
        self.lineEdit_CurrentState.setText(str(self.imapSession.getCurrentState()))
        self.cb_intercepted.setChecked(self.imapSession.intercepted)
        self.cb_intercepted.stateChanged.connect(self.cb_intercepted_changed)

        self.tableView_SessionHistory.setModel(self.imapSession.history)
        self.tableView_SessionHistory.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_SessionHistory.setSelectionBehavior(QTableView.SelectRows)
        self.tableView_SessionHistory.setSelectionMode(QTableView.SingleSelection)

        if self.qProxyThread:
            self.qProxyThread.sigSessionHistoryChanged.connect(self.proxyThreadSignalUpdateHistoryTable)
            self.qProxyThread.sigStateChanged.connect(self.proxyThreadStateChanged)

        self.tableView_SessionHistory.selectionModel().selectionChanged.connect(self.tv_SessionHistory_selectionChanged)

        #Tab 2
        self.button_SendNewCommand.clicked.connect(self.button_NewCommand_SendCommand_click)

    def closeEvent(self, evnt):
        self.sigClose.emit(self.row)
        return

    def sendCommandThreadFinished(self):
        self.button_SendNewCommand.setEnabled(True)

    def proxyThreadSignalUpdateHistoryTable(self):
        self.imapSession.history.layoutChanged.emit()
        if self.currentTag:
            self.updateCommandSpecificWidgets(self.currentTag)

    def proxyThreadStateChanged(self):
        self.lineEdit_CurrentState.setText(self.imapSession.getCurrentState())

    def cb_intercepted_changed(self, state):
        self.imapSession.intercepted = self.cb_intercepted.isChecked()

    def tv_SessionHistory_selectionChanged(self, selected, deselected):
        if selected:
            self.currentTag = self.imapSession.historyGetHistoryAsList()[selected.indexes()[0].row()]
            self.updateCommandSpecificWidgets(self.currentTag)
        else:
            self.currentTag = None

    def button_NewCommand_SendCommand_click(self):
        self.button_SendNewCommand.setEnabled(False)

        commandText = self.plainTextEdit_NewCommand.toPlainText()
        convertLFToCRLF = self.checkBox_NewCommand_ConvertLF.isChecked()

        self.sendThread = SendLocalCommandThread(self, commandText, convertLFToCRLF)
        self.sendThread.sigFinished.connect(self.sendCommandThreadFinished)
        self.sendThread.start()


    def updateCommandSpecificWidgets(self, tag):
        command, response = self.imapSession.historyGetTupleByTag(tag)

        self.plainTextEdit_CommandRaw.clear()
        self.plainTextEdit_Reponse_Raw.clear()
        self.treeWidget_CommandTree.clear()
        self.treeWidget_ResponseTree.clear()

        if command:
            self.plainTextEdit_CommandRaw.setPlainText(command.getRaw())
            tree = command.getParsingTree()
            if tree:
                self.treeWidget_CommandTree.addTopLevelItem(larkTreeToQtTreeWidgetItem(tree))
                self.treeWidget_CommandTree.expandAll()
        if response:
            self.plainTextEdit_Reponse_Raw.setPlainText(response.getRaw())
            tree = response.getParsingTree()
            if tree:
                self.treeWidget_ResponseTree.addTopLevelItem(larkTreeToQtTreeWidgetItem(tree))
                self.treeWidget_ResponseTree.expandAll()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QDialog()

    imap = ImapSession()
    imap.clientPeer = '127.0.0.1:5678'
    imap.serverPeer = '127.0.0.1:143'

    w = AppSessionWindow(dialog, imap)
    dialog.show()
    sys.exit(app.exec_())
