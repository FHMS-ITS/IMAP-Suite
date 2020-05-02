from qt_utils.qt_utils import larkTreeToQtTreeWidgetItem
from qt_generated.gui_pendingDialog import Ui_PendingDialog
from qt_utils.qt_QThreads import ParserThread
from imap.Imap4rev1Parser import Imap4Rev1Parser
from utils.imap_constants import *

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem


class AppPendingDialog(QDialog, Ui_PendingDialog):
    sigClose = pyqtSignal(str)

    def __init__(self, imapSession):
        super(AppPendingDialog, self).__init__(None)
        self.startingRules = PARSING_STARTING_RULES
        self.imapSession = imapSession
        self.parsingThread = None

        if imapSession.interceptedCommand:
            self.messageString = imapSession.currentCommandLine
        else:
            self.messageString = imapSession.responseBuffer

        self.setupUi(self)

        self.setWindowFlag(Qt.CustomizeWindowHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.cb_Parser.addItems(self.startingRules)

        self.lineEdit_ClientPeer.setText(str(self.imapSession.clientPeer))
        self.lineEdit_ServerPeer.setText(str(self.imapSession.serverPeer))
        self.lineEdit_CurrentState.setText(str(self.imapSession.getCurrentState()))

        self.plainTextEdit_CommandRaw.setPlainText(self.messageString)

        self.button_Parse.clicked.connect(self.button_Parse_click)
        self.button_Forward.clicked.connect(self.button_Forward_click)

    def parsingThreadParsingDone(self):
        treeList, rest = self.parsingThread.result

        self.treeWidget_CommandTree.clear()
        for tree in treeList:
            self.treeWidget_CommandTree.addTopLevelItem(larkTreeToQtTreeWidgetItem(tree))

        if rest != '':
            treeRest = QTreeWidgetItem()
            treeRest.setText(0, QTREE_REST)
            treeRest.setText(1, rest)
            self.treeWidget_CommandTree.addTopLevelItem(treeRest)
        self.treeWidget_CommandTree.setColumnWidth(0, 250)
        self.treeWidget_CommandTree.expandAll()

        self.parsingThread = None

        self.button_Parse.setEnabled(True)

    def button_Parse_click(self):
        if self.parsingThread:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Still parsing...")
            msg.setWindowTitle("Parser busy")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        else:
            raw = self.plainTextEdit_CommandRaw.toPlainText()
            startingRule = self.cb_Parser.currentText()
            convertLFToCRLF = self.checkBox_ConvertLF.isChecked()

            if convertLFToCRLF:
                raw = raw.replace('\n', '\r\n')

            self.parsingThread = ParserThread(raw, Imap4Rev1Parser(startingRule))

            self.parsingThread.sigParsingDone.connect(self.parsingThreadParsingDone)
            self.parsingThread.start()

            self.button_Parse.setEnabled(False)

    def button_Forward_click(self):
        raw = self.plainTextEdit_CommandRaw.toPlainText()
        convertLFToCRLF = self.checkBox_ConvertLF.isChecked()
        if convertLFToCRLF:
            raw = raw.replace('\n', '\r\n')

        if self.imapSession.interceptedCommand:
            self.imapSession.currentCommandLine = raw
        else:
            self.imapSession.responseBuffer = raw

        self.imapSession.mutex.release()
        self.imapSession.interceptedCommand = False
        self.close()