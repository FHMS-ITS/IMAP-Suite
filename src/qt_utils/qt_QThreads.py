from imap.imap_proxy import startProxy
from imap.ImapSession import ImapSession
from utils.parser_utils import parse
from PyQt5.QtCore import QThread, pyqtSignal
from utils.imap_constants import *

import socket
import select


class SendLocalCommandThread(QThread):
    sigFinished = pyqtSignal()

    def __init__(self, appWindow, commandText, convertLFToCRLF):
        QThread.__init__(self)
        self.appWindow = appWindow
        self.raw = commandText
        self.convertLFToCRLF = convertLFToCRLF

    def run(self):
        if self.convertLFToCRLF:
            self.raw = self.raw.replace('\n', '\r\n')
            print(self.raw.encode(ENCODING))

        self.appWindow.imapSession.sendCommandToLocalSocket(self.raw)

        self.appWindow.button_SendNewCommand.setEnabled(True)
        self.sigFinished.emit()

class StopProxyThread(QThread):
    def __init__(self, appWindow):
        QThread.__init__(self)
        self.appWindow = appWindow

    def run(self):
        self.appWindow.proxyThread.wait()
        print('MainThread: ProxyThread exited')
        self.appWindow.proxyThread = None

        self.appWindow.ui.button_StartProxy.setEnabled(True)
        self.appWindow.ui.button_StopProxy.setEnabled(False)
        self.appWindow.ui.button_testProxyConfig.setEnabled(True)
        self.appWindow.ui.lineEdit_LocalBindAddress.setEnabled(True)
        self.appWindow.ui.lineEdit_ServerConnectionString.setEnabled(True)

class TestProxyConfigThread(QThread):
    sigTestProxyError = pyqtSignal('PyQt_PyObject')
    sigTestProxySuccess = pyqtSignal()

    def __init__(self, localAddress, serverAddress):
        QThread.__init__(self)
        self.result = None
        self.localAddress = localAddress
        self.serverAddress = serverAddress

    def __del__(self):
        self.wait()

    def run(self):
        # test local binding address:
        success = True
        try:
            localIP, localPort = self.localAddress.split(':', 1)
            print('setup sockets: start')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('setup sockets: success')

            print('setting socket options: start')
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('setting socket options: success')

            print('bind and listen on client-side: start')
            s.bind((localIP, int(localPort)))
            print('bind and listen on client-side: success')

            print('closing socket: start')
            s.close()
            print('closing socket: success')

        except Exception as ex:
            success = False
            self.sigTestProxyError.emit('Local listening Address:\n' + str(ex))


        # test if Server address is correct and an IMAP Server
        try:
            remoteIP, remotePort = self.serverAddress.split(':', 1)
            print('connecting to server: start')
            to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            to_server.connect((remoteIP, int(remotePort)))
            print('connecting to server: success')

            readable, writeable, errors = select.select([to_server], [], [], 3)
            imapSession = ImapSession(s_to_server=to_server)
            trees = imapSession.readGreetingfromServer()

            if trees:
                print('Greeting received!')

        except Exception as ex:
            success = False
            self.sigTestProxyError.emit('Server Address:\n' + str(ex))

        if success is True:
            self.sigTestProxySuccess.emit()

class ParserThread(QThread):
    sigParsingDone = pyqtSignal()

    def __init__(self, raw, parser):
        QThread.__init__(self)
        self.raw = raw
        self.parser = parser
        self.result = None

    def __del__(self):
        self.wait()

    def run(self):
        self.result = parse(self.parser, self.raw)
        self.sigParsingDone.emit()

class ProxyThread(QThread):
    sigNewSession = pyqtSignal()
    sigStateChanged = pyqtSignal()
    sigSessionHistoryChanged = pyqtSignal()
    sigInterception = pyqtSignal('PyQt_PyObject')

    def __init__(self, threadListModel, localAddress, serverAddress, intercepted):
        QThread.__init__(self)
        self.abortThread = False
        self.threadListModel = threadListModel
        self.localAddress = localAddress
        self.serverAddress = serverAddress
        self.intercepted = intercepted

    def run(self):
        startProxy(self, self.threadListModel, self.localAddress, self.serverAddress)