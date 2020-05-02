from PyQt5.QtCore import QAbstractTableModel, Qt


class ImapSessionListModel(QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super(ImapSessionListModel, self).__init__(*args, **kwargs)
        self.sessionList = []
        self.headerData = ['Client', 'Server', 'Current State']

    def __str__(self):
        return str(self.rowCount(1))

    def data(self, index, role):
        if role == Qt.DisplayRole:
            column = index.column()
            if column == 0: #Client
                return str(self.sessionList[index.row()].clientPeer)
            elif column == 1: #Server
                return str(self.sessionList[index.row()].serverPeer)
            elif column == 2: #Current State
                return str(self.sessionList[index.row()].getCurrentState())

    def rowCount(self, index):
        return len(self.sessionList)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerData[section]

    def addItem(self, imapSession):
        self.sessionList.append(imapSession)

    def getItem(self, index):
        return self.sessionList[index.row()]

    def emptySessionList(self):
        self.sessionList = []

class ImapSessionHistoryTableModel(QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super(ImapSessionHistoryTableModel, self).__init__(*args, **kwargs)
        self.commandList = dict()
        self.headerData = ['Tag', 'has Command', 'has Response']

    def __str__(self):
        return str(self.rowCount(1))

    def data(self, index, role):
        if role == Qt.DisplayRole:
            currentTag = list(self.commandList)[index.row()]
            currentObject = self.commandList[currentTag]
            column = index.column()
            if column == 0: #Tag
                return str(currentTag)
            elif column == 1: #has Command
                if currentObject[0]:
                    command = currentObject[0].getCommand()
                    if command == '':
                        return str('-')
                    else:
                        return str(command)
                else:
                    return str(False)
            elif column == 2: #has Response
                if currentObject[1]:
                    return currentObject[1].getResponseResult()
                else:
                    return str(False)

    def rowCount(self, index):
        return len(self.commandList)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerData[section]