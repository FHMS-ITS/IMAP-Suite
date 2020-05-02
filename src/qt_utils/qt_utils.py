from PyQt5.QtWidgets import QTreeWidgetItem
from utils.imap_constants import *

import lark

def larkTreeToQtTreeWidgetItem(larkTree, parent=None):
    result = None
    if parent:
        result = QTreeWidgetItem(parent, parent.type())
    else:
        result = QTreeWidgetItem()

    if isinstance(larkTree, lark.Tree):
        result.setText(0, larkTree.data)
        for child in larkTree.children:
            if isinstance(child, lark.Token):
                token = QTreeWidgetItem(result, result.type())

                if str(child) == ' ':
                    token.setText(0, QTREE_SP)
                    token.setText(1, ' ')
                elif str(child) == '\r':
                    token.setText(0, QTREE_CR)
                    token.setText(1, '\\r')
                elif str(child) == '\n':
                    token.setText(0, QTREE_LF)
                    token.setText(1, '\\n')
                elif str(child) == '\r\n':
                    token.setText(0, QTREE_CRLF)
                    token.setText(1, '\\r\\n')
                else:
                    token.setText(0, QTREE_TOKEN)
                    token.setText(1, str(child))
                result.addChild(token)
            else: # child is lark.tree
                ruleName = child.data
                if ruleName in ('astring_char', 'atom', 'quoted', 'nil', 'tag', 'text', 'number', 'nz_number', 'flag', 'date_time'):
                    tmp = QTreeWidgetItem(result, result.type())
                    tmp.setText(0, ruleName)
                    tmp.setText(1, tree_to_string(child))
                    result.addChild(tmp)
                elif ruleName == 'literal':
                    literal = QTreeWidgetItem(result, result.type())
                    literal.setText(0, 'literal')
                    token1 = QTreeWidgetItem(literal, literal.type())
                    token1.setText(0, QTREE_TOKEN)
                    token1.setText(1, '{')
                    number = QTreeWidgetItem(literal, literal.type())
                    number.setText(0, 'number')
                    number.setText(1, tree_to_string(child.children[1]))
                    token2 = QTreeWidgetItem(literal, literal.type())
                    token2.setText(0, QTREE_TOKEN)
                    token2.setText(1, '}')

                    datachar8 = ''
                    for char in child.children[3:]:
                        datachar8 += str(char)

                    char8Data = QTreeWidgetItem(literal, literal.type())
                    char8Data.setText(0, QTREE_CHAR8STAR)
                    char8Data.setText(1, datachar8)

                    literal.addChild(token1)
                    literal.addChild(number)
                    literal.addChild(token2)
                    literal.addChild(char8Data)

                    result.addChild(literal)
                else:
                    result.addChild(larkTreeToQtTreeWidgetItem(child, result))

    return result

def tree_to_string(tree):
    data = ""
    if isinstance(tree, lark.Tree):
        for subtree in tree.children:
            data = data + tree_to_string(subtree)
    else:
        data = str(tree)
    return data