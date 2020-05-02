#!/usr/bin/python3

import socket
import select
import _thread
import traceback

from imap.ImapSession import ImapSession, ImapResponse, ImapCommand, ImapGreeting
from utils.imap_constants import *

def getNextCommandForwardOtherResponses(imapSession):
    to_client = imapSession.getSocketClient()
    to_server = imapSession.getSocketServer()
    localSocket = imapSession.getSocketLocal()

    rlist = [to_client, to_server, localSocket]
    wlist = []
    xlist = []
    commands = []

    while (True):
        readable, writeable, errors = select.select(rlist, wlist, xlist)

        try:
            if to_server in readable:
                print('to_server')
                responses = imapSession.readResponsefromServer()
                for tree in responses: #Schicke alle vollständigen Responses an den Client
                    imapResponse = ImapResponse()
                    response = imapSession.getTransformer().transform(tree)

                    if imapSession.checkIfTagIsInjected(response.getTag()) is False:
                        imapSession.sendStringToClient(response)

                    imapResponse.setParsingTree(tree)
                    imapResponse.setResponseObject(response)
                    imapResponse.setRaw(str(response))

                    imapSession.historyAddResponseToCommandByTag(response.getTag(), imapResponse)

            if to_client in readable:
                print('to_client')
                trees = imapSession.readCommandFromClient()

                if trees:
                    for tree in trees:
                        imapCommand = ImapCommand()
                        commandObject = imapSession.getTransformer().transform(tree)
                        commands.append(commandObject)
                        imapCommand.setTag(commandObject.getTag())
                        imapCommand.setCommand(commandObject.getName())
                        imapCommand.setCommandObject(commandObject)
                        imapCommand.setParsingTree(tree)
                        imapCommand.setRaw(str(commandObject))
                        imapSession.historyAppendCommand(imapCommand)

                elif trees == []:
                    errorCommand = ImapCommand(raw=imapSession.currentCommandLine)
                    errorResponse = ImapResponse(raw=UNKNOWN_COMMAND_RESPONSE)
                    imapSession.resetCommandBuffer()
                    #errorResponse.reparseRaw() #kann nicht geparsed werden...
                    imapSession.sendStringToClient(errorResponse.raw)
                    imapSession.historyAppendError((errorCommand, errorResponse))

            if localSocket in readable:
                print('localSocket')
                trees = imapSession.readCommandFromLocalSocket()
                if trees:
                    for tree in trees:
                        imapCommand = ImapCommand()
                        commandObject = imapSession.getTransformer().transform(tree)
                        commands.append(commandObject)
                        imapCommand.setTag(commandObject.getTag())
                        imapCommand.setCommand(commandObject.getName())
                        imapCommand.setCommandObject(commandObject)
                        imapCommand.setParsingTree(tree)
                        imapCommand.setRaw(str(commandObject))
                        imapSession.historyAppendCommand(imapCommand)

                        imapSession.appendInjectedCommandTag(commandObject.getTag())

                elif trees == []:
                    errorCommand = ImapCommand(raw=imapSession.currentCommandLine)
                    errorResponse = ImapResponse(raw=UNKNOWN_COMMAND_RESPONSE)
                    imapSession.historyAppendError((errorCommand, errorResponse))

            return commands
        except Exception as ex:
            print('Daten konnten nicht geparsed werden!')
            print('EXCEPTION: ' + str(ex))
            print('Stacktrace:')
            traceback.print_exc()

def getNextResponseForTagForwardOtherResponses(imapSession, tag):
    responses = imapSession.readResponsefromServer()
    if responses is not None:
        result = None
        for tree in responses:

            response = imapSession.getTransformer().transform(tree)
            curr_response_tag = response.getTag()

            if curr_response_tag == tag:
                result = response
            elif imapSession.checkIfTagIsInjected(curr_response_tag) is False:
                    imapSession.sendStringToClient(response)

            imapResponse = ImapResponse()
            imapResponse.setParsingTree(tree)
            imapResponse.setResponseObject(response)
            imapResponse.setRaw(str(response))

            imapSession.historyAddResponseToCommandByTag(curr_response_tag, imapResponse)
        return result
    else:
        return None

def idling(imapSession, idleCommandTag):
    to_client = imapSession.getSocketClient()
    to_server = imapSession.getSocketServer()

    rlist = [to_client, to_server]
    wlist = []
    xlist = []
    commands = []

    doneRecv = False

    while (True):
        readable, writeable, errors = select.select(rlist, wlist, xlist)

        try:
            if to_server in readable:
                print('idle_to_server')
                responses = imapSession.readUntaggedResponsefromServer()
                for tree in responses:
                    imapResponse = ImapResponse()
                    response = imapSession.getTransformer().transform(tree)

                    imapResponse.setParsingTree(tree)
                    imapResponse.setResponseObject(response)
                    imapResponse.setRaw(str(response))

                    imapSession.historyAddResponseToCommandByTag(idleCommandTag, imapResponse)
                    imapSession.sendStringToClient(str(response))

            if to_client in readable:
                print('idle_to_client')
                trees = imapSession.readDoneFromClient()

                if trees:
                    for tree in trees:
                        doneCommand = imapSession.getTransformer().transform(tree)
                        imapSession.historyAppendRawToCommandByTag(idleCommandTag, str(doneCommand))
                        imapSession.sendStringToServer(str(doneCommand))
                        doneRecv = True

                elif trees == []:
                    errorCommand = ImapCommand(raw=imapSession.currentCommandLine)
                    errorResponse = ImapResponse(raw=UNKNOWN_COMMAND_RESPONSE)
                    imapSession.resetCommandBuffer()
                    # errorResponse.reparseRaw() #kann nicht geparsed werden...
                    imapSession.sendStringToClient(errorResponse.raw)
                    imapSession.historyAppendError((errorCommand, errorResponse))

            return doneRecv
        except Exception as ex:
            print('Daten konnten nicht geparsed werden!')
            print('EXCEPTION: ' + str(ex))
            print('Stacktrace:')
            traceback.print_exc()

def handleConnection(name, imapSession):
    serverIP, serverPort = imapSession.serverAddressString.split(':', 1)

    print('connecting to server: start')
    to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    to_server.connect((serverIP, int(serverPort)))
    print('connecting to server: success')

    imapSession.setTo_Server(to_server)

    imapSession.setupLocalSocket()

    pendingCommandTag = None

    while (imapSession.abortThread == False):
        current_state = imapSession.getCurrentState()
        print('Current State: ' + str(current_state))
        if current_state == WAIT_FOR_GREETING:
            trees = imapSession.readGreetingfromServer()

            if trees:
                imapGreeting = ImapGreeting()

                greeting = imapSession.getParserGreeting().transform(trees[0])
                imapSession.sendStringToClient(greeting)

                cond = greeting.getCondition()
                if cond == COND_BYE:
                    imapSession.stateMachineTransitDisconnect()
                elif cond == COND_OK:
                    imapSession.stateMachineTransitGreeting()
                elif cond == 'PREAUTH':
                    imapSession.stateMachineTransitPreauth()

                imapGreeting.setParsingTree(trees[0])
                imapGreeting.setGreetingObject(greeting)
                imapGreeting.setRaw(str(greeting))

                imapSession.historyAppendGreeting(imapGreeting)
                continue

        elif current_state == NOT_AUTH:
            commands = getNextCommandForwardOtherResponses(imapSession)
            if commands is not None:
                for command in commands:

                    name = command.getName()
                    if name == 'LOGIN':
                        imapSession.stateMachineTransitAuth_Login()
                    elif name == 'AUTHENTICATE':
                        imapSession.stateMachineTransitAuth_Plain()
                    imapSession.sendCommandObjectToServer(command)
                    currentTag = command.getTag()

        elif current_state == AUTH:
            commands = getNextCommandForwardOtherResponses(imapSession)

            if commands is not None:
                for command in commands:

                    name = command.getName()

                    if name in ['SELECT', 'EXAMINE']:
                        pendingCommandTag = command.getTag()
                        imapSession.stateMachineTransitSelect_Examine()
                    elif name == 'IDLE':
                        pendingCommandTag = command.getTag()
                        imapSession.stateMachineTransitIdle()


                    imapSession.sendCommandObjectToServer(command)

        elif current_state == SELECTED_PENDING:
            response = getNextResponseForTagForwardOtherResponses(imapSession, pendingCommandTag)

            if response:
                pendingCommandTag = None
                cond = response.getResponseCode()
                if cond == COND_OK:
                    imapSession.stateMachineTransitSelect_Examine_Ok()
                elif cond == COND_NO:
                    imapSession.stateMachineTransitSelect_Examine_No()

                if imapSession.checkIfTagIsInjected(response.getTag()) is False:
                    imapSession.sendStringToClient(response)

        elif current_state == SELECTED:
            commands = getNextCommandForwardOtherResponses(imapSession)

            if commands is not None:
                for command in commands:

                    name = command.getName()

                    if name == 'CLOSE':
                        imapSession.stateMachineTransitClose()
                    elif name == 'LOGOUT':
                        imapSession.stateMachineTransitLogout()
                    elif name == 'IDLE':
                        pendingCommandTag = command.getTag()
                        imapSession.stateMachineTransitIdle()

                    imapSession.sendCommandObjectToServer(command)

        elif current_state == AUTH_WAIT_FOR_CONT_REQ:
            trees = imapSession.readContReqfromServer()
            if trees:
                cont_req = imapSession.getParserContReq().transform(trees[0])
                imapSession.sendStringToClient(cont_req)
                imapSession.stateMachineTransitAuth_Con_Req()
                imapSession.historyAppendRawToResponseByTag(currentTag, str(cont_req))
                continue
            else:
                print(AUTH_WAIT_FOR_CONT_REQ + ': Error')

        elif current_state == AUTH_WAIT_FOR_BASE64:
            trees = imapSession.readBase64fromClient()
            if trees:
                base64 = imapSession.getParserBase64().transform(trees[0])
                imapSession.sendStringToServer(base64 + '\r\n')
                imapSession.stateMachineTransitAuth_Base64()
                imapSession.historyAppendRawToCommandByTag(currentTag, str(base64 + '\r\n'))
                continue
            else:
                print(AUTH_WAIT_FOR_BASE64 + ': Error')

        elif current_state == AUTH_CHECK:
            trees = imapSession.readResponsefromServer()
            if trees:
                for response in trees:
                    resp = imapSession.getParserResponse().transform(response)
                    if imapSession.checkIfTagIsInjected(resp.getTag()) is False:
                        imapSession.sendStringToClient(resp)
                    imapResponseObject = ImapResponse(tree=response, responseObject=resp, raw=str(resp))
                    code = resp.getResponseCode()
                    if code == None: # response_fatal, server closing connection
                        print(AUTH_CHECK + ' response_fatal:' + resp.decode(ENCODING))
                    elif code == COND_OK:
                        imapSession.stateMachineTransitAuth_Ok()
                    elif code == COND_NO:
                        imapSession.stateMachineTransitAuth_No()
                    else:
                        print(AUTH_CHECK + ' response_done:' + resp.decode(ENCODING))
                        imapSession.stateMachineTransitAuth_No()
                    if currentTag:
                        imapSession.historyAddResponseToCommandByTag(currentTag, imapResponseObject)
                        currentTag = None
                continue
        elif current_state == IDLE_AUTH:
            doneRecv = idling(imapSession, pendingCommandTag)
            if doneRecv:
                pendingCommandTag = None
                imapSession.stateMachineTransitIdleDone()
            continue

        elif current_state == IDLE_SELECTED:
            doneRecv = idling(imapSession, pendingCommandTag)
            if doneRecv:
                pendingCommandTag = None
                imapSession.stateMachineTransitIdleDone()
            continue
        else:
            #State Disconnected
            imapSession.quitSession()
    imapSession.quitSession()


def startProxy(qProxyThread, threadListModel, localAddress, serverAddress):
    localIP, localPort = localAddress.split(':', 1)

    print('setup sockets: start')
    main_to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('setup sockets: success')

    print('setting socket options: start')
    main_to_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('setting socket options: success')

    print('bind and listen on client-side: start')
    main_to_client.bind((localIP, int(localPort)))
    main_to_client.settimeout(10)
    main_to_client.listen(1)

    print('bind and listen on client-side: success')

    i = 0

    threadList = []

    while (qProxyThread.abortThread == False):
        try:
            print('waiting for connections...')
            new_to_client, client_addr = main_to_client.accept()
            print('connection from ', client_addr)

            imapSession = ImapSession(qProxyThread=qProxyThread, s_to_client=new_to_client, serverAddressString=serverAddress, intercepted=qProxyThread.intercepted)
            threadListModel.addItem(imapSession)
            print('startProxy: ' + str(threadListModel))
            qProxyThread.sigNewSession.emit()

            threadList.append(_thread.start_new_thread(handleConnection, (i, imapSession)))
            i = i + 1
        except socket.timeout:
            pass
    print('Proxy closing...')
    main_to_client.close()
    print('main socket closed...')
    for sess in threadListModel.sessionList:
        sess.abortThread = True

if __name__ == "__main__":
    startProxy()