#!/usr/bin/python3

from lark import Lark, exceptions

from utils.AbstractParser import AbstractParser
from imap.Imap4rev1Transformer import Imap4rev1Transformer

import traceback


class MultipleMsg(Exception):
    def __init__(self, pos_in_stream):
        self.pos_in_stream = pos_in_stream

    def __str__(self):
        return 'Multiple messages in input detected. Try splitting at: ' + str(self.pos_in_stream)

class UnexpectedEndOfInput(Exception):
    def __init__(self, expected):
        self.expected = expected

    def __str__(self):
        return 'Got EOF but expecting: ' + str(self.expected)

class Imap4Rev1Parser(AbstractParser):
    def __init__(self, start):
        self.start = start
        self.l_ci = Lark(r'''					
            						address         : "(" addr_name SP addr_adl SP addr_mailbox SP addr_host ")"
                                    addr_adl        : nstring
                                    addr_host       : nstring
                                    addr_mailbox    : nstring
                                    addr_name       : nstring
                                    append          : "APPEND"i SP mailbox [SP flag_list] [SP date_time] SP literal
                                    astring         : astring_char+ | string
                                    astring_char    : ATOM_CHAR | resp_specials
                                    atom            : ATOM_CHAR+
                                    ATOM_CHAR       : /[\x21|\x23-\x24|\x26-\x27|\x2B-\x5B|\x5E-\x7A|\x7C-\x7E]/
                                    atom_specials   : "(" | ")" | "{" | SP | CTL | list_wildcards | quoted_specials | resp_specials
                                    authenticate    : "AUTHENTICATE"i SP auth_type (CRLF base64)*
                                    auth_type       : atom
                                    !base64.1        : (base64_char~4)* [base64_terminal]
                                    base64_char.1   : ALPHA | DIGIT | "+" | "/"
                                    base64_terminal.1: (base64_char~2 "==") | (base64_char~3 "=")
                                    body            : "(" (body_type_1part | body_type_mpart) ")"
                                    body_extension  : nstring | number | "(" body_extension (SP body_extension)* ")"
                                    body_ext_1part  : body_fld_md5 [SP body_fld_dsp [SP body_fld_lang [SP body_fld_loc (SP body_extension)*]]]
                                    body_ext_mpart  : body_fld_param [SP body_fld_dsp [SP body_fld_lang [SP body_fld_loc (SP body_extension)*]]]
                                    body_fields     : body_fld_param SP body_fld_id SP body_fld_desc SP body_fld_enc SP body_fld_octets
                                    body_fld_desc   : nstring
                                    body_fld_dsp    : "(" string SP body_fld_param ")" | nil
                                    body_fld_enc    : (DQUOTE ("7BIT"i | "8BIT"i | "BINARY"i | "BASE64"i | "QUOTED_PRINTABLE"i) DQUOTE) | string
                                    body_fld_id     : nstring
                                    body_fld_lang   : nstring | "(" string (SP string)* ")"
                                    body_fld_loc    : nstring
                                    body_fld_lines  : number
                                    body_fld_md5    : nstring
                                    body_fld_octets : number
                                    body_fld_param  : "(" string SP string (SP string SP string)* ")" | nil
                                    body_type_1part : (body_type_basic | body_type_msg | body_type_text) [SP body_ext_1part]
                                    body_type_basic : media_basic SP body_fields
                                    body_type_mpart : body+ SP media_subtype [SP body_ext_mpart]
                                    body_type_msg   : media_message SP body_fields SP envelope SP body SP body_fld_lines
                                    body_type_text  : media_text SP body_fields SP body_fld_lines
                                    capability      : ("AUTH="i auth_type) | atom
                                    capability_data.1: "CAPABILITY"i (SP capability)* SP "IMAP4rev1"i (SP capability)*
                                    CHAR8           : /[\x01-\xFF]/
                                    charset         : atom | quoted
                                    command         : tag SP (command_any | command_auth | command_nonauth | command_select) CRLF
                                    command_any     : "CAPABILITY"i | "LOGOUT"i | "NOOP"i | x_command
                                    command_auth    : append | create | delete | examine | list | lsub | rename | select | status | subscribe | unsubscribe | idle
                                    command_nonauth : login | authenticate | "STARTTLS"i
                                    command_select  : "CHECK"i | "CLOSE"i | "EXPUNGE"i | copy | fetch | store | uid | search
                                    continue_req    : "+" SP (resp_text | base64) CRLF
                                    copy            : "COPY"i SP sequence_set SP mailbox
                                    create          : "CREATE"i SP mailbox
                                    date            : date_text | DQUOTE date_text DQUOTE
                                    date_day        : DIGIT~1..2
                                    date_day_fixed  : (SP DIGIT) | DIGIT~2
                                    date_month      : "Jan" | "Feb" | "Mar" | "Apr" | "May" | "Jun" | "Jul" | "Aug" | "Sep" | "Oct" | "Nov" | "Dec"
                                    date_text       : date_day "-" date_month "-" date_year
                                    date_year       : DIGIT~4
                                    date_time       : DQUOTE date_day_fixed "-" date_month "-" date_year SP time SP zone DQUOTE
                                    delete          : "DELETE"i SP mailbox
                                    digit_nz        : /[\x31-\x39]/
                                    done            : "DONE"i CRLF
                                    envelope        : "(" env_date SP env_subject SP env_from SP env_sender SP env_reply_to SP env_to SP env_cc SP env_bcc SP env_in_reply_to SP env_message_id ")"
                                    env_bcc         : "(" address+ ")" | nil
                                    env_cc          : "(" address+ ")" | nil
                                    env_date        : nstring
                                    env_from        : "(" address+ ")" | nil
                                    env_in_reply_to : nstring
                                    env_message_id  : nstring
                                    env_reply_to    : "(" address+ ")" | nil
                                    env_sender      : "(" address+ ")" | nil
                                    env_subject     : nstring
                                    env_to          : "(" address+ ")" | nil
                                    examine         : "EXAMINE"i SP mailbox
                                    fetch           : "FETCH"i SP sequence_set SP ("ALL"i | "FULL"i | "FAST"i | fetch_att | "(" fetch_att (SP fetch_att)* ")")
                                    fetch_att       : "ENVELOPE"i | "FLAGS"i | "INTERNALDATE"i | "RFC822"i [".HEADER"i | ".SIZE"i | ".TEXT"i] | "BODY"i ["STRUCTURE"i] | "UID"i | "BODY"i section ["<" number "." nz_number ">"] | "BODY.PEEK"i section ["<" number "." nz_number ">"]
                                    flag            : "\Answered" | "\Flagged" | "\Deleted" | "\Seen" | "\Draft" | flag_keyword | flag_extension
                                    flag_extension  : /[\\]/ atom
                                    flag_fetch      : flag | "\Recent"
                                    flag_keyword    : atom
                                    flag_list       : "(" [flag (SP flag)*] ")"
                                    flag_perm       : flag | "\*"
                                    greeting        : "*" SP (resp_cond_auth | resp_cond_bye) CRLF
                                    header_fld_name : astring
                                    header_list     : "(" header_fld_name (SP header_fld_name)* ")"
                                    idle            : "IDLE"i
                                    list            : "LIST"i SP mailbox SP list_mailbox
                                    list_mailbox    : list_char+ | string
                                    list_char       : ATOM_CHAR | list_wildcards | resp_specials
                                    list_wildcards  : "%" | "*"
                                    literal         : "{" number "}" CRLF CHAR8*
                                    login           : "LOGIN"i SP userid SP password
                                    lsub            : "LSUB"i SP mailbox SP list_mailbox
                                    mailbox         : "INBOX"i | astring
                                    mailbox_data    :  "FLAGS"i SP flag_list | "LIST"i SP mailbox_list | "LSUB"i SP mailbox_list | "SEARCH"i (SP nz_number)* | "STATUS"i SP mailbox SP "(" [status_att_list] ")" | number SP "EXISTS"i | number SP "RECENT"i
                                    mailbox_list    : "(" [mbx_list_flags] ")" SP (DQUOTE quoted_char DQUOTE | nil) SP mailbox
                                    mbx_list_flags  : (mbx_list_oflag SP)* mbx_list_sflag (SP mbx_list_oflag)* | mbx_list_oflag (SP mbx_list_oflag)*
                                    mbx_list_oflag  : "\Noinferiors" | flag_extension
                                    mbx_list_sflag  : "\Noselect" | "\Marked" | "\Unmarked"
                                    media_basic     : ((DQUOTE ("APPLICATION"i | "AUDIO"i | "IMAGE"i | "MESSAGE"i | "VIDEO"i) DQUOTE) | string) SP media_subtype
                                    media_message   : DQUOTE "MESSAGE"i DQUOTE SP DQUOTE "RFC822"i DQUOTE
                                    media_subtype   : string
                                    media_text      : DQUOTE ("TEXT"i) DQUOTE SP media_subtype
                                    message_data    : nz_number SP ("EXPUNGE"i | ("FETCH"i SP msg_att))
                                    msg_att         : "(" (msg_att_dynamic | msg_att_static) (SP (msg_att_dynamic | msg_att_static))* ")"
                                    msg_att_dynamic : "FLAGS"i SP "(" [flag_fetch (SP flag_fetch)*] ")"
                                    msg_att_static  : "ENVELOPE"i SP envelope | "INTERNALDATE"i SP date_time | "RFC822"i [".HEADER"i | ".TEXT"i] SP nstring | "RFC822.SIZE"i SP number | "BODY"i ["STRUCTURE"i] SP body | "BODY"i section ["<" number ">"] SP nstring | "UID"i SP uniqueid
                                    nil             : "NIL"i
                                    nstring         : string | nil
                                    number          : DIGIT+
                                    nz_number       : digit_nz DIGIT*
                                    password        : astring
                                    quoted          : DQUOTE quoted_char* DQUOTE
                                    quoted_char     : (/[\x01-\x09|\x0B-\x0C|\x0E-\x21|\x23-\x5B|\]-\x7F]/) | /[\\]/ quoted_specials
                                    quoted_specials : DQUOTE | /[\\]/
                                    rename          : "RENAME"i SP mailbox SP mailbox
                                    response        : (continue_req | response_data)* response_done
                                    response_data.1 : "*" SP (resp_cond_state | resp_cond_bye | mailbox_data | message_data | capability_data) CRLF
                                    response_done   : response_tagged | response_fatal
                                    response_fatal  : "*" SP resp_cond_bye CRLF
                                    response_tagged : tag SP resp_cond_state CRLF
                                    response_untagged: (continue_req | response_data)*
                                    resp_cond_auth  : ("OK"i | "PREAUTH"i) SP resp_text
                                    resp_cond_bye   : "BYE"i SP resp_text
                                    resp_cond_state : ("OK"i | "NO"i | "BAD"i) SP resp_text
                                    resp_specials   : "]"
                                    resp_text.2     : ["[" resp_text_code "]" SP] text
                                    resp_text_code.1: "ALERT"i | "BADCHARSET"i [SP "(" charset (SP charset)* ")" ] | capability_data | "PARSE"i | "PERMANENTFLAGS"i SP "(" [flag_perm (SP flag_perm)*] ")" | "READ_ONLY"i | "READ_WRITE"i | "TRYCREATE"i | "UIDNEXT"i SP nz_number | "UIDVALIDITY"i SP nz_number | "UNSEEN"i SP nz_number | atom [SP (/[\x01-\x09|\x0B-\x0C|\x0E-\x5C|\x5E-\x7F]/)+]
                                    search          : "SEARCH"i [SP "CHARSET"i SP charset] (SP search_key)+
                                    search_key      : "ALL"i | "ANSWERED"i | "BCC"i SP astring | "BEFORE"i SP date | "BODY"i SP astring | "CC"i SP astring | "DELETED"i | "FLAGGED"i | "FROM"i SP astring | "KEYWORD"i SP flag_keyword | "NEW"i | "OLD"i | "ON"i SP date | "RECENT"i | "SEEN"i | "SINCE"i SP date | "SUBJECT"i SP astring | "TEXT"i SP astring | "TO"i SP astring | "UNANSWERED"i | "UNDELETED"i | "UNFLAGGED"i | "UNKEYWORD"i SP flag_keyword | "UNSEEN"i | "DRAFT"i | "HEADER"i SP header_fld_name SP astring | "LARGER"i SP number | "NOT"i SP search_key | "OR"i SP search_key SP search_key | "SENTBEFORE"i SP date | "SENTON"i SP date | "SENTSINCE"i SP date | "SMALLER"i SP number | "UID"i SP sequence_set | "UNDRAFT"i | sequence_set | "(" search_key (SP search_key)* ")"
                                    section         : "[" [section_spec] "]"
                                    section_msgtext : "HEADER"i | "HEADER.FIELDS"i [".NOT"i] SP header_list | "TEXT"i
                                    section_part    : nz_number ("." nz_number)*
                                    section_spec    : section_msgtext | (section_part ["." section_text])
                                    section_text    : section_msgtext | "MIME"i
                                    select          : "SELECT"i SP mailbox
                                    seq_number      : nz_number | "*"
                                    seq_range       : seq_number ":" seq_number
                                    sequence_set    : (seq_number | seq_range) ["," sequence_set]
                                    status          : "STATUS"i SP mailbox SP "(" status_att (SP status_att)* ")"
                                    status_att      : "MESSAGES"i | "RECENT"i | "UIDNEXT"i | "UIDVALIDITY"i | "UNSEEN"i
                                    status_att_val  : ("MESSAGES"i SP number) | ("RECENT"i SP number) | ("UIDNEXT"i SP nz_number) | ("UIDVALIDITY"i SP nz_number) | ("UNSEEN"i SP number)
                                    status_att_list :  status_att_val (SP status_att_val)*
                                    store           : "STORE"i SP sequence_set SP store_att_flags
                                    store_att_flags : (["+" | "-"] "FLAGS"i [".SILENT"i]) SP (flag_list | (flag (SP flag)*))
                                    string          : quoted | literal
                                    subscribe       : "SUBSCRIBE"i SP mailbox
                                    tag             : (/[\x21|\x23-\x24|\x26-\x27|\x2C-\x5B|\]-\x7A|\x7C-\x7E]/)+
                                    text.2          : TEXT_CHAR+
                                    TEXT_CHAR       : /[\x01-\x09|\x0B-\x0C|\x0E-\x7F]/
                                    time            : DIGIT~2 ":" DIGIT~2 ":" DIGIT~2
                                    uid             : "UID"i SP (copy | fetch | search | store)
                                    uniqueid        : nz_number
                                    unsubscribe     : "UNSUBSCRIBE"i SP mailbox
                                    userid          : astring
                                    x_command       : "X" atom
                                    zone            : ("+" | "-") DIGIT~4

                                    CTL             : /[\x00-\x1F|\x7F]/
                                    DQUOTE          : /[\x22]/
                                    CRLF            : CR LF


            						%import common.WS_INLINE -> SP
            						%import common.CR
            						%import common.LF
            						%import common.DIGIT
            						%import common.LETTER    -> ALPHA
            					  ''', start=self.start, keep_all_tokens=True)

        self.l = self.l_ci


    def parse_input(self, input_string):
        if input_string is not None:
            result = None
            try:

                print(input_string)
                result = self.l.parse(input_string)

            except exceptions.UnexpectedCharacters as ex:
                print('####### UnexpectedCharacter: ' + str(self.start))
                #print(ex)
                #print(ex.get_context(input_string))
                #print(str(ex.allowed))
                if not ex.allowed:
                    print('Multiple Messages!')
                    raise MultipleMsg(ex.pos_in_stream)
                elif ex.allowed:
                    raise UnexpectedEndOfInput(ex.allowed)
                result = None
            except exceptions.UnexpectedEOF as ex:
                raise UnexpectedEndOfInput(ex.expected)
            except Exception as ex:
                print('####### Exception: ' + str(self.start))
                print(ex)
                traceback.print_exc()
                result = None
                raise ex
            return result

    def transform(self, tree):
        if tree is not None:
            return Imap4rev1Transformer().transform(tree)