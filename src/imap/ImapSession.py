from imap.Imap4rev1StateMachine import ImapMachine
from utils.parser_utils import parse
from imap.Imap4rev1Parser import Imap4Rev1Parser
from imap.Imap4rev1Transformer import Imap4rev1Transformer
from qt_utils.qt_ViewModels import ImapSessionHistoryTableModel
from imap.IMAP4rev1Classes import Response

from datetime import datetime
from utils.imap_constants import *

import _thread
import re
import socket
import random
import string

class ImapCommand():
    def __init__(self, tag='', commandText='', tree=None, commandObject=None, raw=''):
        self.timestamp = datetime.now()
        self.tag = tag
        self.commandText = commandText
        self.parsingTree = tree
        self.commandObject = commandObject
        self.raw = raw

    def setTag(self, tag):
        self.tag = tag

    def setCommand(self, command):
        self.commandText = command

    def setParsingTree(self, tree):
        self.parsingTree = tree

    def setCommandObject(self, commandObject):
        self.commandObject = commandObject

    def setRaw(self, raw):
        self.raw = raw

    def getTag(self):
        return self.tag

    def getCommand(self):
        return self.commandText

    def getParsingTree(self):
        return self.parsingTree

    def getCommandObject(self):
        return self.commandObject

    def getRaw(self):
        return self.raw

    def reparseRaw(self):
        self.parsingTree = None
        self.responseObject = None
        parser = Imap4Rev1Parser('command')
        try:
            self.tree = parser.parse_input(self.raw)
            if self.tree:
                self.responseObject = parser.transform(self.tree)
        except Exception as ex:
            print('reparsing failed: ' + str(self.raw))


class ImapResponse():
    def __init__(self, tree=None, responseObject=None, raw=''):
        self.timestamp = datetime.now()
        self.parsingTree = tree
        self.responseObject = responseObject
        self.raw = raw

    def setParsingTree(self, tree):
        self.parsingTree = tree

    def setResponseObject(self, responseObject):
        self.responseObject = responseObject

    def setRaw(self, raw):
        self.raw = raw

    def getParsingTree(self):
        return self.parsingTree

    def getResponseObject(self):
        return self.responseObject

    def getRaw(self):
        return self.raw

    def getResponseResult(self):
        if self.responseObject:
            if isinstance(self.responseObject, Response):
                return str(self.responseObject.getResponseCode())
            else:
                return str('-')
        else:
            return str('-')

    def reparseRaw(self):
        self.parsingTree = None
        self.responseObject = None
        parser = Imap4Rev1Parser('response')
        try:
            #print(self.raw.encode('utf-8'))
            self.parsingTree = parser.parse_input(self.raw)
            if self.parsingTree:
                self.responseObject = parser.transform(self.parsingTree)
        except Exception as ex:
            print('reparsing failed: ' + str(self.raw))

class ImapGreeting():
    def __init__(self, tree=None, greetingObject=None, raw=''):
        self.timestamp = datetime.now()
        self.parsingTree = tree
        self.greetingObject = greetingObject
        self.raw = raw

    def setParsingTree(self, tree):
        self.parsingTree = tree

    def setGreetingObject(self, greetingObject):
        self.greetingObject = greetingObject

    def setRaw(self, raw):
        self.raw = raw

    def getParsingTree(self):
        return self.parsingTree

    def getGreetingObject(self):
        return self.greetingObject

    def getRaw(self):
        return self.raw

    def getResponseResult(self):
        if self.greetingObject:
            return str(self.greetingObject.getCondition())
        else:
            return str('-')

class ImapInputStream():
    def __init__(self):
        self.buffer = b''

    def write(self, input):
        self.buffer += input

    def readLine(self):
        splits = self.buffer.split(b'\r\n')
        if len(splits) == 1: #kein \r\n im buffer
            return None
        else:
            self.buffer = self.buffer[len(splits[0]) + 2:]
            return splits[0] + b'\r\n'

    def readBytes(self, count):
        if len(self.buffer) >= count:
            result = self.buffer[:count]
            self.buffer = self.buffer[count:]
        else:
            result = self.buffer
            self.buffer = b''
        return result

    def hasData(self):
        if len(self.buffer) > 0:
            return True
        else:
            return False

    def reset(self):
        self.buffer = b''

class ImapSession():
    def __init__(self, qProxyThread=None, s_to_client=None, s_to_server=None, serverAddressString=None, intercepted=False):
        self.abortThread = False
        self.qProxyThread = qProxyThread
        self.serverAddressString = serverAddressString
        self.literalLength = None
        self.intercepted = intercepted
        self.interceptedCommand = False

        self.mutex = _thread.allocate_lock()
        self.mutex.acquire()

        self.to_client = s_to_client
        self.to_server = s_to_server

        self.localSocket = None

        self.injectedCommandTags = []

        self.clientPeer = None
        self.serverPeer = None

        self.greeting_parser = Imap4Rev1Parser('greeting')
        self.response_parser = Imap4Rev1Parser('response')
        self.untagged_response_parser = Imap4Rev1Parser('response_untagged')
        self.command_parser = Imap4Rev1Parser('command')
        self.cont_req_parser = Imap4Rev1Parser('continue_req')
        self.base64_parser = Imap4Rev1Parser('base64')
        self.done_parser = Imap4Rev1Parser('done')

        self.imapTransformer = Imap4rev1Transformer()

        self.imapMachine = ImapMachine()

        self.commandBuffer = ImapInputStream()
        self.currentCommandLine = ''
        self.responseBuffer = ''

        self.commandList = []
        self.responseList = []

        #Dictionary mit key:value --> tag: (command, response)
        #wenn Reponse noch Pending --> tag: (command, None)
        #wenn Tag { erhält, ist es eine out-of-order Response (bspw. Greeting) --> tag: (None, response)
        #Spezialfall {greeting --> tag: (None, greeting)
        self.history = ImapSessionHistoryTableModel()
        self.outOfOrderResponseCounter = 0

        self.updatePeerInfos()

    def __str__(self):
        result = ''
        if self.clientPeer:
            result += 'Client: ' + str(self.clientPeer)
        else:
            result += 'Client: not connected'

        if self.serverPeer:
            result += ' / Server: ' + str(self.serverPeer)
        else:
            result += ' / Server: not connected'
        return result

    def interceptConnection(self, isCommand):
        if self.intercepted and self.qProxyThread:
            if isCommand:
                self.interceptedCommand = True
            self.qProxyThread.sigInterception.emit(self)
            self.mutex.acquire()

    def setupLocalSocket(self):
        self.localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.localSocketAddress = 'sockets/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.localSocket.bind(self.localSocketAddress)

    def setTo_Client(self, s):
        self.to_client = s
        self.updatePeerInfos()

    def setTo_Server(self, s):
        self.to_server = s
        self.updatePeerInfos()

    def updateUI(self):
        self.qProxyThread.sigSessionHistoryChanged.emit()

    def updatePeerInfos(self):
        if self.clientPeer is None:
            if self.to_client:
                self.clientPeer = self.to_client.getpeername()
        if self.serverPeer is None:
            if self.to_server:
                self.serverPeer = self.to_server.getpeername()

    def appendInjectedCommandTag(self, tag):
        self.injectedCommandTags.append(tag)

    def checkIfTagIsInjected(self, tag):
        return tag in self.injectedCommandTags

    def historyPrint(self):
        print('Saved-History:')
        for tag, tuple in self.history.commandList.items():
            command = False
            response = False
            if tuple[0]:
                command = True
            if tuple[1]:
                response = True
            print('Tag: ' + str(tag) + ' Command: ' + str(command) + ' Response: ' + str(response))

    def historyAppendCommand(self, command):
        tag = command.tag
        if tag in self.history.commandList:
            print('Tag ' + tag + 'already used!!!')
        else:
            self.history.commandList[tag] = (command, None)
            self.updateUI()

    def historyGetTupleByTag(self, tag):
        #None, wenn Tag nicht exisitert
        return self.history.commandList[tag]

    def historyGetHistoryAsList(self):
        return list(self.history.commandList)

    def historyAddResponseToCommandByTag(self, tag, newResponse):
        if tag in self.history.commandList:
            command, response = self.history.commandList[tag]
            if response:
                response.raw += newResponse.getRaw()
                response.reparseRaw()
                self.updateUI()
            else:
                self.history.commandList[tag] = (command, newResponse)
            self.updateUI()
        else:
            print('Tag ' + tag + 'not found!!!')

    def historyAppendRawToResponseByTag(self, tag, raw):
        if tag in self.history.commandList:
            command, response = self.history.commandList[tag]
            if response:
                response.raw += raw
            else:
                response = ImapResponse(raw=raw)
            response.reparseRaw()
            self.history.commandList[tag] = (command, response)
            self.updateUI()
        else:
            print('Tag ' + tag + 'not found!!!')

    def historyAppendRawToCommandByTag(self, tag, raw):
        if tag in self.history.commandList:
            command, response = self.history.commandList[tag]
            command.raw += raw
            command.reparseRaw()
            self.history.commandList[tag] = (command, response)
            self.updateUI()
        else:
            print('Tag ' + tag + 'not found!!!')

    def historyAppendOutOfOrderResponse(self, response):
        self.outOfOrderResponseCounter = self.outOfOrderResponseCounter + 1
        tag = '{' + str(self.outOfOrderResponseCounter)
        self.history.commandList[tag] = (None, response)
        self.updateUI()

    def historyAppendError(self, tuple):
        self.outOfOrderResponseCounter = self.outOfOrderResponseCounter + 1
        tag = '{{' + str(self.outOfOrderResponseCounter)
        self.history.commandList[tag] = tuple
        self.updateUI()

    def historyAppendGreeting(self, greeting):
        tag = '{greeting'
        if tag in self.history.commandList:
            print('Greeting already exists!!!')
        else:
            self.history.commandList[tag] = (None, greeting)
            self.updateUI()

    def readGreetingfromServer(self):
        data = self.readDatafromSocket(self.to_server).decode(ENCODING)
        if data:
            self.responseBuffer += data
        self.interceptConnection(False)
        trees, self.responseBuffer = parse(self.greeting_parser, self.responseBuffer)
        return trees

    def readContReqfromServer(self):
        data = self.readDatafromSocket(self.to_server).decode(ENCODING)
        if data:
            self.responseBuffer += data
        self.interceptConnection(False)
        trees, self.responseBuffer = parse(self.cont_req_parser, self.responseBuffer)
        return trees

    def readResponsefromServer(self):
        data = self.readDatafromSocket(self.to_server).decode(ENCODING)
        if data:
            self.responseBuffer += data
        self.interceptConnection(False)
        trees, self.responseBuffer = parse(self.response_parser, self.responseBuffer)
        return trees

    def readUntaggedResponsefromServer(self):
        data = self.readDatafromSocket(self.to_server).decode(ENCODING)
        if data:
            self.responseBuffer += data
        self.interceptConnection(False)
        trees, self.responseBuffer = parse(self.untagged_response_parser, self.responseBuffer)
        return trees

    def readBase64fromClient(self):
        data = self.readDatafromSocket(self.to_client)
        if data:
            self.commandBuffer.write(data)

        if self.commandBuffer.hasData():
            base64 = self.commandBuffer.readLine().decode(ENCODING)
            if base64:
                #self.interceptConnection(True)
                trees, tmp = parse(self.base64_parser, base64[:-2]) # das \r\n kann vom base64-Parser nicht geparsed werden, da es zum Command gehört.
                return trees
        return None

    def checkIfLineEndsWithLiteral(self, string):
        if len(string) >= 5:
            if string[-1] == '\n':
                if string[-2] == '\r':
                    if string[-3] == '}':
                        result = ''
                        for i in range(4, len(string)):
                            if string[-i].isdigit():
                                result = string[-i] + result
                            elif string[-i] == '{':
                                return int(result)
                            else:
                                return None
        return None

        #pattern = re.compile("{([0-9]+)}\r\n")
        match = re.search(r"{([0-9]+)}\r\n$", string)
        if match:
            return int(match.group(1))
        else:
            return None

    def checkIfLineEndsWithCRLF(self, string):
        if len(string) >= 2:
            if string[-1] == '\n':
                if string[-2] == '\r':
                    return True
        return False

    def readCommandFromClient(self):
        data = self.readDatafromSocket(self.to_client)
        if data:
            self.commandBuffer.write(data)

        literalData = b''

        while self.commandBuffer.hasData():
            if self.literalLength == None:
                self.currentCommandLine += self.commandBuffer.readLine().decode(ENCODING)

                if self.checkIfLineEndsWithCRLF(self.currentCommandLine):
                    self.literalLength = self.checkIfLineEndsWithLiteral(self.currentCommandLine)
                    if self.literalLength:
                        self.sendStringToClient('+ \r\n')
                        continue
                    else: #Nun müsste der Command vollständig gelesen worden sein
                        self.interceptConnection(True)

                        trees, tmp = parse(self.command_parser, self.currentCommandLine)
                        self.currentCommandLine = ''
                        return trees

            else:
                literalData += self.commandBuffer.readBytes(self.literalLength)
                self.literalLength -= len(literalData)
                self.currentCommandLine += literalData.decode(ENCODING)

                if self.literalLength == 0:
                    self.literalLength = None
                    literalData = b''

                continue

    def readDoneFromClient(self):
        data = self.readDatafromSocket(self.to_client)
        if data:
            self.commandBuffer.write(data)

        while self.commandBuffer.hasData():
            self.currentCommandLine += self.commandBuffer.readLine().decode(ENCODING)

            if self.checkIfLineEndsWithCRLF(self.currentCommandLine):
                self.interceptConnection(True)

                trees, tmp = parse(self.done_parser, self.currentCommandLine)
                self.currentCommandLine = ''
                return trees

    def readCommandFromLocalSocket(self):
        data = self.readDatafromSocket(self.localSocket).decode(ENCODING)
        trees, tmp = parse(self.command_parser, data)
        return trees

    def sendCommandToLocalSocket(self, string):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.connect(self.localSocketAddress)
        s.send(string.encode(ENCODING))

    def readDatafromSocket(self, s):
        BUFFERSIZE = 64*1024
        data = s.recv(BUFFERSIZE)
        if not data:
            if s == self.to_client:
                print('disconnect from client: ', str(self.clientPeer))
            elif s == self.to_server:
                print('disconnect from server: ', str(self.serverPeer))
            self.quitSession()
        else:
            return data#.decode(ENCODING)

    def quitSession(self):
        print('SessionThread is exiting ')
        if self.to_client:
            self.to_client.close()
            self.to_client = None
        if self.to_server:
            self.to_server.close()
            self.to_server = None
        self.stateMachineTransitDisconnect()
        _thread.exit()

    def getSocketClient(self):
        return self.to_client

    def getSocketServer(self):
        return self.to_server

    def getSocketLocal(self):
        return self.localSocket

    def sendCommandObjectToServer(self, command):
        data = str(command)
        splits = data.split('\r\n')
        if len(splits) == 1:
            self.sendStringToServer(data)
        else:
            waitForContReq = False
            for line in splits[:-1]:
                if waitForContReq:
                    trees = self.readContReqfromServer()
                    if trees:
                        contReq = self.getTransformer().transform(trees[0])
                        self.historyAppendRawToResponseByTag(command.getTag(), str(contReq))
                        waitForContReq = False
                    else:
                        #ToDo: was passiert, wenn kein ContReq empfangen wurde?
                        continue
                line = line + '\r\n'
                if self.checkIfLineEndsWithLiteral(line):
                    waitForContReq = True
                self.sendStringToServer(line)

    def sendStringToClient(self, string):
        if self.to_client:
            data = str(string).encode(ENCODING)
            self.to_client.send(data)

    def sendStringToServer(self, string):
        data = str(string).encode(ENCODING)
        self.to_server.send(data)

    def getParserGreeting(self):
        return self.greeting_parser

    def getParserResponse(self):
        return self.response_parser

    def getParserCommand(self):
        return self.command_parser

    def getParserContReq(self):
        return self.cont_req_parser

    def getParserBase64(self):
        return self.base64_parser

    def getTransformer(self):
        return self.imapTransformer

    def getCurrentState(self):
        return self.imapMachine.current_state.identifier

    def getImapMachine(self):
        return self.imapMachine

    def getCommandBuffer(self):
        return self.commandBuffer

    def resetCommandBuffer(self):
        self.commandBuffer.reset()

    def stateMachineTransitGreeting(self):
        self.imapMachine.greeting()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitPreauth(self):
        self.imapMachine.preauth()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_Login(self):
        self.imapMachine.auth_login()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_Plain(self):
        self.imapMachine.auth_plain()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_Con_Req(self):
        self.imapMachine.auth_con_req()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_Base64(self):
        self.imapMachine.auth_base64()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_Ok(self):
        self.imapMachine.auth_ok()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitAuth_No(self):
        self.imapMachine.auth_no()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitSelect_Examine(self):
        self.imapMachine.select_examine()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitSelect_Examine_Ok(self):
        self.imapMachine.select_examine_ok()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitSelect_Examine_No(self):
        self.imapMachine.select_examine_no()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitIdle(self):
        self.imapMachine.getIdleTransition(self.getCurrentState())()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitIdleDone(self):
        self.imapMachine.getIdleDoneTransition(self.getCurrentState())()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitClose(self):
        self.imapMachine.close()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitLogout(self):
        self.imapMachine.logout()
        self.qProxyThread.sigStateChanged.emit()

    def stateMachineTransitDisconnect(self):
        self.imapMachine.getDisconnectTransition(self.getCurrentState())()
        self.qProxyThread.sigStateChanged.emit()


