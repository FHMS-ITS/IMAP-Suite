
def toString(x):
    if x == None:
        return 'NIL'
    else:
        return str(x)

class AbstractCommand():
    def __init__(self, name):
        if name == None:
            raise Exception('Unknown Command')
        else:
            self.name = str(name)

    def __str__(self):
        return str(self.name)

class SimpleCommandWithMailbox(AbstractCommand):
    #CREATE, DELETE, EXAMINE, SELECT, SUBSCRIBE, UNSUBSCRIBE
    def __init__(self, command, mailbox):
        self.name = command
        self.mailbox = mailbox

    def __str__(self):
        return str(self.name) + ' ' + str(self.mailbox)

class Address():
    def __init__(self, name, adl, mailbox, host):
        self.name = name
        self.adl = adl
        self.mailbox = mailbox
        self.host = host

    def __str__(self):
        result = '('

        if self.name == None:
            result = result + 'NIL'
        else:
            result = result + self.name

        result += ' '

        if self.adl == None:
            result = result + 'NIL'
        else:
            result = result + self.adl

        result += ' '

        if self.mailbox == None:
            result = result + 'NIL'
        else:
            result = result + self.mailbox

        result += ' '

        if self.host == None:
            result = result + 'NIL'
        else:
            result = result + self.host

        result += ')'
        return result

class Append(AbstractCommand):
    def __init__(self, mailbox, flag_list, date_time, literal):
        self.name = 'APPEND'
        self.mailbox = mailbox
        self.flag_list = flag_list
        self.date_time = date_time
        self.literal = literal

    def __str__(self):
        result = str(self.name)
        result = result + ' ' + str(self.mailbox)
        if self.flag_list != None:
            result = result + ' ' + str(self.flag_list)
        if self.date_time != None:
            result = result + ' ' + str(self.date_time)
        result = result + ' ' + str(self.literal)
        return result

class Authenticate(AbstractCommand):
    def __init__(self, auth_type, base64_list):
        self.name = 'AUTHENTICATE'
        self.auth_type = auth_type
        self.base64_list = base64_list

    def __str__(self):
        result = str(self.name) + ' ' + str(self.auth_type)
        for element in self.base64_list:
            result = result + '\r\n' + str(element)
        return result

class Body():
    def __init__(self, body_type):
        self.body_type = body_type

    def __str__(self):
        return '(' + str(self.body_type) + ')'

class Body_Ext_1Part():
    def __init__(self, md5, dsp, lang, loc, ext_list):
        self.md5 = md5
        self.dsp = dsp
        self.lang = lang
        self.loc = loc
        self.ext_list = ext_list

    def __str__(self):
        result = str(self.md5)
        if self.dsp != None:
            result = result + ' ' + str(self.dsp)
            if self.lang != None:
                result = result + ' ' + str(self.lang)
                if self.loc != None:
                    result = result + ' ' + str(self.loc)
                    if self.ext_list != None:
                        for i in self.ext_list:
                            result = result + ' ' + str(i)
        return result

class Body_Ext_MPart():
    def __init__(self, param, dsp, lang, loc, ext_list):
        self.param = param
        self.dsp = dsp
        self.lang = lang
        self.loc = loc
        self.ext_list = ext_list

    def __str__(self):
        result = str(self.param)
        if self.dsp != None:
            result = result + ' ' + str(self.dsp)
            if self.lang != None:
                result = result + ' ' + str(self.lang)
                if self.loc != None:
                    result = result + ' ' + str(self.loc)
                    if self.ext_list != None:
                        for i in self.ext_list:
                            result = result + ' ' + str(i)
        return result

class Body_Extension():
    def __init__(self, ext_list):
        self.ext_list = ext_list

    def __str__(self):
        result = '('
        for i in self.ext_list:
            result = result + str(i) + ' '

        result = result[:-1] + ')'
        return result

class Body_Fields():
    def __init__(self, param, id, desc, enc, octets):
        self.param = param
        self.id = id
        self.desc = desc
        self.enc = enc
        self.octets = octets

    def __str__(self):
        return toString(self.param) + ' ' + toString(self.id) + ' ' + toString(self.desc) + ' ' + toString(self.enc) + ' ' + toString(self.octets)

class Body_Fld_Dsp():
    def __init__(self, string, param):
        self.string = string
        self.param = param

    def __str__(self):
        return '(' + str(self.string) + ' ' + str(self.param) + ')'

class Body_Fld_Lang():
    def __init__(self, string_list):
        self.string_list = string_list

    def __str__(self):
        result = '('
        for i in self.string_list:
            result = result + str(i) + ' '

        result = result[:-1] + ')'
        return result

class Body_Fld_Param():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = '('
        for att, val in self.list:
            result = result + '"' + str(att) + '" "' + str(val) + '" '

        result = result[:-1] + ')'
        return result

class Body_Type_1Part():
    def __init__(self, body_type, body_ext):
        self.body_type = body_type
        self.body_ext = body_ext

    def __str__(self):
        result = str(self.body_type)
        if self.body_ext != None:
            result = result + ' ' + str(self.body_ext)

        return result

class Body_Type_MPart():
    def __init__(self, body_list, subtype, ext_mpart):
        self.body_list = body_list
        self.subtype = subtype
        self.ext_mpart = ext_mpart

    def __str__(self):
        result = ''
        for i in self.body_list:
            result = result + str(i)
        result = result + ' ' + str(self.subtype)
        if self.ext_mpart != None:
            result = result + ' ' + str(self.ext_mpart)
        return result

class Body_Type_Basic():
    def __init__(self, media, fields):
        self.media = media
        self.fields = fields

    def __str__(self):
        return str(self.media) + ' ' + str(self.fields)

class Body_Type_Msg():
    def __init__(self, message, fields, envelope, body, lines):
        self.message = message
        self.fields = fields
        self.envelope = envelope
        self.body = body
        self.lines = lines

    def __str__(self):
        return str(self.message) + ' ' + str(self.fields) + ' ' + str(self.envelope) + ' ' + str(self.body) + ' ' + str(self.lines)

class Body_Type_Text():
    def __init__(self, text, fields, lines):
        self.text = text
        self.fields = fields
        self.lines = lines

    def __str__(self):
        return str(self.text) + ' ' + str(self.fields) + ' ' + str(self.lines)

class Capability_Data():
    def __init__(self, cap_list):
        self.supported_caps = {'capability',
                               'imap4rev1',
                               'auth=plain',
                               'auth=login',
                               'idle'
                               }
        self.cap_list = []
        for element in cap_list:
            if element.lower() in self.supported_caps:
                self.cap_list.append(element)

    def __str__(self):
        result = 'CAPABILITY'
        for element in self.cap_list:
            result = result + ' ' + str(element)
        return result

class Command():
    def __init__(self, tag, command):
        self.tag = tag
        self.command = command

    def __str__(self):
        return str(self.tag) + ' ' + str(self.command) + '\r\n'

    def getName(self):
        return self.command.name

    def getTag(self):
        return self.tag

    def getCommand(self):
        return self.command

class Continue_Req():
    def __init__(self, text, base64):
        self.text =  text
        self.base64 = base64

    def __str__(self):
        result = '+' + ' '
        if self.text != None:
            result = result + str(self.text)
        else:
            result = result + str(self.base64)
        return result + '\r\n'

class Copy(AbstractCommand):
    def __init__(self, seq_set, mailbox):
        self.name = 'COPY'
        self.seq_set = seq_set
        self.mailbox = mailbox

    def __str__(self):
        return str(self.name) + ' ' + str(self.seq_set) + ' ' + str(self.mailbox)

class Date():
    def __init__(self, quoted, date_text):
        self.quoted = quoted
        self.date_text = date_text

    def __str__(self):
        if self.quoted == True:
            return '"' + str(self.date_text) + '"'
        else:
            return str(self.date_text)

class Date_Text():
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    def __str__(self):
        return str(self.day) + '-' + str(self.month) + '-' + str(self.year)

class Date_Time():

    def __init__(self, day, month, year, time, zone):
        self.day = day
        self.month = month
        self.year = year
        self.time = time
        self.zone = zone

    def __str__(self):
        return '"' + self.day + '-' + self.month + '-' + self.year + ' ' + self.time + ' ' + self.zone + '"'

class Envelope():
    def __init__(self, date, subject, env_from, sender, reply_to, to, cc, bcc, in_reply_to, message_id):
        self.date = date
        self.subject = subject
        self.env_from = env_from
        self.sender = sender
        self.reply_to = reply_to
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.in_reply_to = in_reply_to
        self.message_id = message_id

    def __str__(self):
        return '(' + str(self.date) + ' ' + str(self.subject) + ' ' + str(self.env_from) + ' ' + str(self.sender) + ' ' + str(self.reply_to) + ' ' + str(self.to) + ' ' + str(self.cc) + ' ' + str(self.bcc) + ' ' + str(self.in_reply_to) + ' ' + str(self.message_id) + ')'

class Env_List():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = '('
        for i in self.list:
            result = result + str(i)
        return result + ')'

class Fetch(AbstractCommand):
    def __init__(self, sequence_set, text, fetch_att, fetch_att_list):
        self.name = 'FETCH'
        self.sequence_set = sequence_set
        self.text = text
        self.fetch_att = fetch_att
        self.fetch_att_list = fetch_att_list

    def __str__(self):
        result = str(self.name) + ' ' + str(self.sequence_set) + ' '
        if self.text != None:
            result = result + str(self.text)
        elif self.fetch_att != None:
            result = result + str(self.fetch_att)
        elif self.fetch_att_list != None:
            result = result + '('
            for element in self.fetch_att_list:
                result = result + str(element) + ' '
            result = result[:-1] + ')'
        return result

    def getFetchAtts(self):
        flags = Fetch_Att('FLAGS', None, None)
        internaldate = Fetch_Att('INTERNALDATE', None, None)
        rfc822_size = Fetch_Att('RFC822.SIZE', None, None)
        envelope = Fetch_Att('ENVELOPE', None, None)
        body = Fetch_Att('BODY', None, None)

        result = []
        if self.text == 'ALL':
            result.extend([flags, internaldate, rfc822_size, envelope])
        elif self.text == 'FAST':
            result.extend([flags, internaldate, rfc822_size])
        elif self.text == 'FULL':
            result.extend([flags, internaldate, rfc822_size, envelope, body])
        elif self.fetch_att is not None:
            result.extend([self.fetch_att])
        else:
            result.extend(self.fetch_att_list)
        return result

class Fetch_Att():
    def __init__(self, text, section, partial):
        self.text = text
        self.section = section
        self.partial = partial

    def __str__(self):
        result = str(self.text)
        if self.section != None:
            result = result + str(self.section)
            if self.partial != None:
                result = result + str(self.partial)
        return result

    def __eq__(self, other):
        if isinstance(other, Section):
            return self.text == other.text and self.section == other.section and self.partial == other.partial
        else:
            return False

    def getText(self):
        return self.text



class Flag_List():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = '('
        for i in self.list:
            result = result + str(i) + ' '
        return result[:-1] + ')'

class Greeting():
    def __init__(self, resp_cond):
        self.resp_cond = resp_cond

    def __str__(self):
        return '*' + ' ' + str(self.resp_cond) + '\r\n'

    def getCondition(self):
        if isinstance(self.resp_cond, Resp_Cond_Bye):
            return 'BYE'
        else:
            return self.resp_cond.cond # OK oder PREAUTH

class Header_List():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = '('
        for i in self.list:
            result = result + str(i) + ' '
        return result[:-1] + ')'

    def __eq__(self, other):
        if isinstance(other, Section):
            return self.list == other.list
        else:
            return False

class Idle(AbstractCommand):
    def __init__(self):
        self.name = 'IDLE'

    def __str__(self):
        return str(self.name)


class List(AbstractCommand):
    def __init__(self, mailbox, list_mailbox):
        self.name = 'LIST'
        self.mailbox = mailbox
        self.list_mailbox = list_mailbox

    def __str__(self):
        return str(self.name) + ' ' + str(self.mailbox) + ' ' + str(self.list_mailbox)

class Literal():
    def __init__(self, length, text):
        if len(text) != int(length):
            #print(len(text))
            #print(int(length))
            #print(text)
            raise Exception("Literal mit falscher Länge, erwartet: " + str(length) + " tatsächlich: " + str(len(text)))
        else:
            self.length = length
            self.text = text

    def __bytes__(self):
        result = b'{' + str(self.length) + b'}' + b'\r\n' + bytes(self.text)
        return result

    def __str__(self):
        return '{' + str(self.length) + '}' + '\r\n' + str(self.text)
        #return '{' + str(self.length) + '}' + '\r\n' + str(self.text.encode('latin1'))[2:-1]
        #return '{' + str(self.length) + '}' + ' CRLF ' + 'LITERAL' + ' #(bytes(...) gibt komplette Bytefolge zurück!)'

class Login(AbstractCommand):
    def __init__(self, userid, password):
        self.name = 'LOGIN'
        self.userid = userid
        self.password = password

    def __str__(self):
        return str(self.name) + ' ' + str(self.userid) + ' ' + str(self.password)

class Lsub(AbstractCommand):
    def __init__(self, mailbox, list_mailbox):
        self.name = 'LSUB'
        self.mailbox = mailbox
        self.list_mailbox = list_mailbox

    def __str__(self):
        return str(self.name) + ' ' + str(self.mailbox) + ' ' + str(self.list_mailbox)

class Mailbox_Data():
    def __init__(self, command, flag_list, mailbox_list, nz_number_list, mailbox, status_att_list, number):
        self.command = command
        self.flag_list = flag_list
        self.mailbox_list = mailbox_list
        self.nz_number_list = nz_number_list
        self.mailbox = mailbox
        self.status_att_list = status_att_list
        self.number = number

    def __str__(self):
        result = ''
        if self.command == 'FLAGS':
            result = str(self.command) + ' ' + str(self.flag_list)
        elif self.command in ('LIST', 'LSUB'):
            result = str(self.command) + ' ' + str(self.mailbox_list)
        elif self.command == 'SEARCH':
            result = str(self.command)
            if self.nz_number_list != None:
                for element in self.nz_number_list:
                    result = result + ' ' + str(element)
        elif self.command == 'STATUS':
            result = str(self.command) + ' ' + str(self.mailbox) + ' ' + '('
            if self.status_att_list != None:
                result = result + str(self.status_att_list)
            result = result + ')'
        elif self.command in ('EXISTS', 'RECENT'):
            result = str(self.number) + ' ' + str(self.command)
        return result

class Mailbox_List():
    def __init__(self, flags, delimiter, mailbox):
        self.flags = flags
        self.delimiter = delimiter
        self.mailbox = mailbox

    def __str__(self):
        result = '(' + str(self.flags) + ')' + ' '
        if self.delimiter != None:
            result = result + '"' + str(self.delimiter) + '"'
        else:
            result = result + 'NIL'
        result = result + ' ' + str(self.mailbox)
        return result

class Mbx_List_Flags():
    def __init__(self, flag_list):
        self.flag_list = flag_list

    def __str__(self):
        result = ''
        for element in self.flag_list:
            result = result + str(element) + ' '
        if result != '':
            result = result[:-1]
        return result

class Media_Basic():
    def __init__(self, type, media_subtype):
        self.type = type
        self.media_subtype = media_subtype

    def __str__(self):
        return str(self.type) + " " + str(self.media_subtype)

class Media_Text():
    def __init__(self, subtype):
        self.subtype = subtype

    def __str__(self):
        return '"TEXT" ' + str(self.subtype)

class Message_Data():
    def __init__(self, nz_number, command, msg_att):
        self.nz_number = nz_number
        self.command = command
        self.msg_att = msg_att

    def __str__(self):
        result = str(self.nz_number) + ' ' + str(self.command)
        if self.command == 'FETCH':
            result = result + ' ' + str(self.msg_att)
        return result

class Msg_Att():
    def __init__(self, msg_att_list):
        self.msg_att_list = msg_att_list

    def __str__(self):
        result = '('
        for element in self.msg_att_list:
            result = result + str(element) + ' '
        result = result[:-1] + ')'
        return result

class Msg_Att_Static():
    def __init__(self, attribute, envelope, date_time, nstring, number, body, section, uniqueid):
        self.attribute = attribute
        self.envelope = envelope
        self.date_time = date_time
        self.nstring = nstring
        self.number = number
        self.body = body
        self.section = section
        self.uniqueid = uniqueid

    def __str__(self):
        result = str(self.attribute) + ' '
        if self.attribute == 'ENVELOPE':
            result = result + str(self.envelope)
        elif self.attribute == 'INTERNALDATE':
            result = result + str(self.date_time)
        elif self.attribute in ('RFC822', 'RFC822.HEADER', 'RFC822.TEXT'):
            result = result + str(self.nstring)
        elif self.attribute == 'RFC822.SIZE':
            result = result + str(self.number)
        elif self.attribute == 'BODYSTRUCTURE':
            result = result + str(self.body)
        elif self.attribute == 'BODY':
            if self.body != None:
                result = result + str(self.body)
            else:
                result = result[:-1] + str(self.section)
                if self.number != None:
                    result = result + '<' + str(self.number) + '>'
                result = result + ' ' + str(self.nstring)
        elif self.attribute == 'UID':
            result = result + str(self.uniqueid)

        return result

class Msg_Att_Dynamic():
    def __init__(self, flag_fetch_list):
        self.flag_fetch_list = flag_fetch_list

    def __str__(self):
        result = 'FLAGS' + ' ' + '('
        if len(self.flag_fetch_list) != 0:
            for element in self.flag_fetch_list:
                result = result + str(element) + ' '
            result = result[:-1]
        result = result + ')'
        return result

class Rename(AbstractCommand):
    def __init__(self, mailbox1, mailbox2):
        self.name = 'RENAME'
        self.mailbox1 = mailbox1
        self.mailbox2 = mailbox2

    def __str__(self):
        return str(self.name) + ' ' + str(self.mailbox1) + ' ' + str(self.mailbox2)

class Resp_Cond_Auth():
    def __init__(self, cond, text):
        self.cond = cond
        self.text = text

    def __str__(self):
        return str(self.cond) + ' ' + str(self.text)

class Resp_Cond_Bye():
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return 'BYE' + ' ' + str(self.text)

class Resp_Cond_State():
    def __init__(self, state, text):
        self.state = state
        self.text = text

    def __str__(self):
        return str(self.state) + ' ' + str(self.text)

class Resp_Text():
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        result = ''
        if self.code != None:
            result = '[' + str(self.code) + ']' + ' '
        result = result + str(self.text)
        return result

class Resp_Text_Code():
    def __init__(self, code, charset_list, capability_data, flag_perm_list, nz_number, other_text):
        self.code = code
        self.charset_list = charset_list
        self.capability_data = capability_data
        self.flag_perm_list = flag_perm_list
        self.nz_number = nz_number
        self.other_text = other_text

    def __str__(self):
        result = ''
        if self.code == None: #capability_data
            result = str(self.capability_data)
        else:
            result = str(self.code)
            if self.code == 'BADCHARSET' and self.charset_list != None:
                result = result + ' ' + '('
                for element in self.charset_list:
                    result = result + str(element) + ' '
                result = result[:-1] + ')'
            elif self.code == 'PERMANENTFLAGS':
                for element in self.flag_perm_list:
                    result = result + ' ' + str(element)
            elif self.code in ('UIDNEXT', 'UIDVALIDITY', 'UNSEEN'):
                result = result + ' ' + str(self.nz_number)
            elif self.code not in ('ALERT', 'PARSE', 'READ-ONLY', 'READ-WRITE', 'TRYCREATE') and self.other_text != None:
                result = result + ' ' + str(self.other_text)
        return result

class Response():
    def __init__(self, list, response_done):
        self.list = list
        self.response_done = response_done

    def __str__(self):
        result = ''
        for element in self.list:
            result = result + str(element)
        result = result + str(self.response_done)
        return result

    def getResponseCode(self):
        result = None
        if isinstance(self.response_done, Response_Tagged):
            result = self.response_done.resp_cond_state.state
        return result

    def getTag(self):
        result = None
        if isinstance(self.response_done, Response_Tagged):
            result = self.response_done.tag
        return result

    def hasBody(self):
        result = False
        for line in self.list:
            if line.message_data is not None:
                if line.message_data.command == 'FETCH':
                    msg_att_list = line.message_data.msg_att.msg_att_list
                    for att in msg_att_list:
                        if isinstance(att, Msg_Att_Static):
                            if att.attribute == 'BODY':
                                if att.section is not None:
                                    result = True
                            elif att.attribute == 'RFC822':
                                result = True

        return result

    def hasRFC822Size(self):
        result = False
        for line in self.list:
            if line.message_data is not None:
                if line.message_data.command == 'FETCH':
                    msg_att_list = line.message_data.msg_att.msg_att_list
                    for att in msg_att_list:
                        if isinstance(att, Msg_Att_Static):
                            if att.attribute == 'RFC822.SIZE':
                                result = True
        return result

class Response_Data():
    def __init__(self, resp_cond_state, resp_cond_bye, mailbox_data, message_data, capability_data):
        self.resp_cond_state = resp_cond_state
        self.resp_cond_bye = resp_cond_bye
        self.mailbox_data = mailbox_data
        self.message_data = message_data
        self.capability_data = capability_data

    def __str__(self):
        result = '*' + ' '
        if self.resp_cond_state != None:
            result = result + str(self.resp_cond_state)
        elif self.resp_cond_bye != None:
            result = result + str(self.resp_cond_bye)
        elif self.mailbox_data != None:
            result = result + str(self.mailbox_data)
        elif self.message_data != None:
            result = result + str(self.message_data)
        elif self.capability_data != None:
            result = result + str(self.capability_data)

        result = result + '\r\n'
        return result

    def getBody(self):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'BODY':
                            if att.section is not None:
                                return att.nstring
                        elif att.attribute == 'RFC822':
                            return att.nstring
        return None

    def setBodyLiteral(self, literal):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'BODY':
                            if att.section is not None:
                                att.nstring = literal

    def setRFC822Literal(self, literal):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'RFC822':
                            att.nstring = literal

    def setRFC822Quoted(self, quoted):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'RFC822':
                            att.nstring = quoted

    def setBodyQuoted(self, quoted):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'BODY':
                            if att.section is not None:
                                att.nstring = quoted


    def getRFC822Size(self):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'RFC822.SIZE':
                            return att.number
        return None

    def setRFC822Size(self, size):
        if self.message_data is not None:
            if self.message_data.command == 'FETCH':
                msg_att_list = self.message_data.msg_att.msg_att_list
                for att in msg_att_list:
                    if isinstance(att, Msg_Att_Static):
                        if att.attribute == 'RFC822.SIZE':
                            att.number = size

class Response_Fatal():
    def __init__(self, resp_cond_bye):
        self.resp_cond_bye = resp_cond_bye

    def __str__(self):
        return '*' + ' ' + str(self.resp_cond_bye) + '\r\n'

class Response_Tagged():
    def __init__(self, tag, resp_cond_state):
        self.tag = tag
        self.resp_cond_state = resp_cond_state

    def __str__(self):
        return str(self.tag) + ' ' + str(self.resp_cond_state) + '\r\n'

class Response_Untagged():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = ''
        for element in self.list:
            result = result + str(element)
        return result

class Search(AbstractCommand):
    def __init__(self, charset, search_key_list):
        self.name = 'SEARCH'
        self.charset = charset
        self.search_key_list = search_key_list

    def __str__(self):
        result = str(self.name)
        if self.charset != None:
            result = result + ' ' + 'CHARSET' + ' ' + str(self.charset)
        for element in self.search_key_list:
            result = result + ' ' + str(element)
        return result

class Search_Key():
    def __init__(self, text, argument):
        self.text = text
        self.argument = argument

    def __str__(self):
        result = str(self.text)
        if self.argument != None:
            result = result + str(self.argument)

        return result

class Section():
    def __init__(self, section_spec):
        self.section_spec = section_spec

    def __str__(self):
        if self.section_spec != None:
            return '[' + str(self.section_spec) + ']'
        else:
            return '[]'

    def __eq__(self, other):
        if isinstance(other, Section):
            return self.section_spec == other.section_spec
        else:
            return False

class Section_Msgtext():
    def __init__(self, text, header_list):
        self.text = text
        self.header_list = header_list

    def __str__(self):
        result = str(self.text)
        if self.header_list != None:
            result = result + ' ' + str(self.header_list)
        return  result

    def __eq__(self, other):
        if isinstance(other, Section_Msgtext):
            return self.text == other.text and self.header_list == other.header_list
        else:
            return False

class Section_Spec():
    def __init__(self, msgtext, part, text):
        self.msgtext = msgtext
        self.part = part
        self.text = text

    def __str__(self):
        if self.msgtext != None:
            return str(self.msgtext)
        else:
            result = str(self.part)
            if self.text != None:
                result = result + '.' + str(self.text)
            return result

    def __eq__(self, other):
        if isinstance(other, Section_Spec):
            return self.msgtext == other.msgtext and self.part == other.part and self.text == other.text
        else:
            return False

class Section_Text():
    def __init__(self, msgtext, text):
        if msgtext == None:
            self.text = text
        elif text == None:
            self.msgtext = msgtext
        else:
            raise Exception('IllegalArgument')

    def __str__(self):
        if self.text == None:
            return str(self.msgtext)
        else:
            return str(self.text)

    def __eq__(self, other):
        if isinstance(other, Section_Text):
            return self.msgtext == other.msgtext and self.text == other.text.text
        else:
            return False

class Status(AbstractCommand):
    def __init__(self, mailbox, status_att_list):
        self.name = 'STATUS'
        self.mailbox = mailbox
        self.status_att_list = status_att_list

    def __str__(self):
        result = str(self.name) + ' ' + str(self.mailbox) + ' ('
        for element in self.status_att_list:
            result = result + str(element) + ' '
        result = result[:-1] + ')'
        return result

class Status_Att_List():
    def __init__(self, list):
        self.list = list

    def __str__(self):
        result = ''
        for element in self.list:
            result = result + str(element) + ' '
        return result[:-1]

class Status_Att_Val():
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def __str__(self):
        return str(self.attribute) + ' ' + str(self.value)

class Store(AbstractCommand):
    def __init__(self, sequence_set, store_att_flags):
        self.name = 'STORE'
        self.sequence_set = sequence_set
        self.store_att_flags = store_att_flags

    def __str__(self):
        return str(self.name) + ' ' + str(self.sequence_set) + ' ' + str(self.store_att_flags)

class UID(AbstractCommand):
    def __init__(self, command):
        self.name = 'UID'
        self.command = command

    def __str__(self):
        return str(self.name) + ' ' + str(self.command)

    def getInsideCommandName(self):
        return self.command.name

    def getInsideCommand(self):
        return self.command