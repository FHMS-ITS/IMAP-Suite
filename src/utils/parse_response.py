#!/usr/bin/python3

from utils.parser_utils import *
from imap.Imap4rev1Parser import *
from imap.ImapSession import ImapSession, ImapInputStream

import socket
import select
import os
import random
import string

test = '1 LOGIN {4}\r\nuser {4}\r\npass\r\n'


data = '2 append "Sent" (\\Seen) "16-Dec-2019 14:48:06 +0100" {11}\r\nEinf\xc3\xbchrung\r\n'

b = b'abc\xc3\xbc\r\n'

print(b)
print(str(b.decode('latin1')))

print(str(b.encode('latin1'))[2:-1])
print(len(b.encode('latin1')))




#l = Imap4Rev1Parser('command')

#tree = l.parse_input(data)
#tree2 = l.transform(tree)
#print(tree.pretty())
#print(test)
#tree = l.parse_input(test)
#tree = l.transform(tree)
#print(tree.pretty())
#print(l.tree_to_string(tree))

#list, rest = parse(l, test)
#print(len(list))
#print('rest: ' + rest)
#for i in list:
#    i = l.transform(i)
#    print(i.pretty())

#print('rest: ' + str(rest))

#buff = ImapInputStream()
#buff.write('abc {27}\r\nasdasd')
#tmp = 'abc {27}\r\n'
#print(str(ImapSession.checkIfLineEndsWithLiteral(ImapSession(), tmp)))

#localSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
#localSocketAddress = 'sockets/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

#os.unlink(localSocketAddress)
#localSocket.bind(localSocketAddress)

#localSocket.listen(1)

#print('selecting...')
#list, tmp, tmp = select.select([localSocket], [], [])
#print('receiving...')
#data = localSocket.recv(1024)


#print(str(data))


