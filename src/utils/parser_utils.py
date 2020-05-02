#!/usr/bin/python3

from imap.Imap4rev1Parser import MultipleMsg, UnexpectedEndOfInput

def parse(parser, input_string):
    tree_list = []
    rest = input_string
    while rest != '':
        try:
            tree_list.append(parser.parse_input(rest))
            # wenn erfolgriech geparsed, beinhaltet rest genau eine Message, kann also leer zurückgegeben werden
            rest = ''

        except MultipleMsg as ex:
            split = ex.pos_in_stream
            tree_list.append(parser.parse_input(rest[:split]))
            rest = rest[split:]

        except UnexpectedEndOfInput as ex:
            return tree_list, rest

    return tree_list, rest