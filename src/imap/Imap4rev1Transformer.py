from lark import Transformer
from imap.IMAP4rev1Classes import *

class Imap4rev1Transformer(Transformer):

    def address(self, args):
        #OPEN BRACKET
        name = args[1]
        #SP
        adl  = args[3]
        #SP
        mail = args[5]
        #SP
        host = args[7]
        #CLOSING BRACKET
        result = Address(name, adl, mail, host)
        return result

    def addr_adl(self, args):
        return args[0]

    def addr_host(self, args):
        return args[0]

    def addr_mailbox(self, args):
        return args[0]

    def addr_name(self, args):
        return args[0]

    def append(self, args):
        flag_list = None
        date_time = None
        literal = None
        argscount = len(args)

        # "APPEND"
        # SP
        mailbox = args[2]
        if argscount == 5:
            literal = args[4]
        elif argscount == 7:
            if isinstance(args[4], Flag_List):
                flag_list = args[4]
            elif isinstance(args[4], Date_Time):
                date_time = args[4]
            literal = args[6]
        else: # argcount == 9
            flag_list = args[4]
            date_time = args[6]
            literal = args[8]
        return Append(mailbox, flag_list, date_time, literal)

    def astring(self, args):
        if len(args) == 1: # string
            return args[0]
        else: # 1*astring-char
            return self.justConcatenateArgs(args)

    def astring_char(self, args):
        return args[0]

    def atom(self, args):
        return self.justConcatenateArgs(args)

    #def atom_specials(self, args): # atom-specials ist auf Grammatikebene bereits in atom hinterlegt, daher überflüssig

    def authenticate(self, args):
        # "AUTHENTICATE"
        # SP
        auth_type = args[2]
        base64_list = []
        for i in range(4, len(args), 2):
            base64_list.append(args[i])

        return Authenticate(auth_type, base64_list)

    def auth_type(self, args):
        return args[0]

    def base64(self, args):
        return self.justConcatenateArgs(args)

    def base64_char(self, args):
        return str(args[0])

    def base64_terminal(self, args):
        return self.justConcatenateArgs(args)

    def body(self, args):
        return Body(args[1])

    def body_ext_1part(self, args):
        argcount = len(args)
        md5 = args[0]
        dsp = None
        lang = None
        loc = None
        ext_list = None
        if argcount >= 3: #SP body-fld-dsp
            #SP
            dsp = args[2]
            if argcount >= 5: #SP body-fld-lang
                #SP
                lang = args[4]
                if argcount >= 7: #SP body-fld-loc
                    #SP
                    loc = args[6]
                    if argcount >= 9: #*(SP body-extension)
                        ext_list = []
                        for i in range(8, argcount, 2):
                            ext_list.append(args[i])

        return Body_Ext_1Part(md5, dsp, lang, loc, ext_list)

    def body_ext_mpart(self, args):
        argcount = len(args)
        param = args[0]
        dsp = None
        lang = None
        loc = None
        ext_list = None
        if argcount >= 3: #SP body-fld-dsp
            #SP
            dsp = args[2]
            if argcount >= 5: #SP body-fld-lang
                #SP
                lang = args[4]
                if argcount >= 7: #SP body-fld-loc
                    #SP
                    loc = args[6]
                    if argcount >= 9: #*(SP body-extension)
                        ext_list = []
                        for i in range(8, argcount, 2):
                            ext_list.append(args[i])

        return Body_Ext_MPart(param, dsp, lang, loc, ext_list)

    def body_extension(self, args):
        if len(args) == 1: #nstring / number
            return args[0]
        else:
            list = []
            # OPEN BRACKET
            for i in range(1, len(args), 2):
                list.append(args[i])
            # CLOSING BRACKET
            return Body_Extension(list)

    def body_fields(self, args):
        param = args[0]
        #SP
        id = args[2]
        #SP
        desc = args[4]
        #SP
        enc = args[6]
        #SP
        octets = args[8]
        return Body_Fields(param, id, desc, enc, octets)

    def body_fld_desc(self, args):
        return args[0]

    def body_fld_dsp(self, args):
        if len(args) == 1: #None
            return args[0]
        else:
            #OPEN BRACKET
            string = args[1]
            #SP
            param = args[3]
            #CLOSING BRACKET
            return Body_Fld_Dsp(string, param)

    def body_fld_enc(self, args):
        if len(args) == 3:
            return self.justConcatenateArgs(args)
        else:
            return args[0]

    def body_fld_id(self, args):
        return args[0]

    def body_fld_lang(self, args):
        if len(args) == 1: #nstring
            return args[0]
        else:
            list = []
            #OPEN BRACKET
            for i in range(1, len(args), 2):
                list.append(args[i])
            #CLOSING BRACKET
            return Body_Fld_Lang(list)

    def body_fld_lines(self, args):
        return args[0]

    def body_fld_loc(self, args):
        return args[0]

    def body_fld_md5(self, args):
        return args[0]

    def body_fld_octets(self, args):
        return args[0]

    def body_fld_param(self, args):
        list = []
        for i in range(1, len(args)-2, 4):
            list.append(((args[i])[1:-1], (args[i+2])[1:-1]))

        return Body_Fld_Param(list)

    def body_type_1part(self, args):
        if len(args) == 1:
            return Body_Type_1Part(args[0], None) #body-type-...
        else:
            return Body_Type_1Part(args[0], args[2]) #SP body-ext-1part

    def body_type_mpart(self, args):
        argcount = len(args)
        body_list = []
        subtype = None
        ext_mpart = None
        if isinstance(args[-1] , Body_Ext_1Part):
            for i in range(0, argcount-4):
                body_list.append(args[i])
            subtype = args[-3]
            ext_mpart = args[-1]
        else:
            for i in range(0, argcount-2):
                body_list.append(args[i])
            subtype = args[-1]


        return Body_Type_MPart(body_list, subtype, ext_mpart)

    def body_type_basic(self, args):
        media = args[0]
        #SP
        fields = args[2]
        return Body_Type_Basic(media, fields)

    def body_type_msg(self, args):
        message = args[0]
        #SP
        fields = args[2]
        #SP
        envelope = args[4]
        #SP
        body = args[6]
        #SP
        lines = args[8]
        return Body_Type_Msg(message, fields, envelope, body, lines)

    def body_type_text(self, args):
        text = args[0]
        #SP
        fields = args[2]
        #SP
        lines = args[4]
        return Body_Type_Text(text, fields, lines)

    def capability_data(self, args):
        cap_list = []
        for i in range(2, len(args), 2):
            cap_list.append(args[i])
        return Capability_Data(cap_list)

    def capability(self, args):
        if len(args) == 2: #AUTH= auth-type
            return str(args[0]) + str(args[1])
        else: #atom
            return str(args[0])

    def charset(self, args):
        return args[0]

    def command(self, args):
        return Command(args[0], args[2])

    def command_any(self, args):
        return AbstractCommand(str(args[0]).upper())

    def command_auth(self, args):
        return args[0]

    def command_nonauth(self, args):
        if str(args[0]).upper() == 'STARTTLS':
            return AbstractCommand('STARTTLS')
        else:
            return args[0]

    def command_select(self, args):
        if str(args[0]).upper() in ('CHECK', 'CLOSE', 'EXPUNGE'):
            return AbstractCommand(str(args[0]))
        else:
            return args[0]

    def continue_req(self, args):
        text = None
        base64 = None
        # "+"
        # SP
        if isinstance(args[2], Resp_Text): #resp-text
            text = args[2]
        else: # base64
            base64 = args[2]
        # CRLF
        return Continue_Req(text, base64)

    def copy(self, args):
        return Copy(args[2], args[4])

    def create(self, args):
        return SimpleCommandWithMailbox('CREATE', args[2])

    def date(self, args):
        if len(args) == 1:
            return Date(False, args[0])
        else:
            return Date(True, args[1])

    def date_day(self, args):
        return self.justConcatenateArgs(args)

    def date_day_fixed(self, args):
        return self.justConcatenateArgs(args)

    def date_text(self, args):
        day = args[0]
        # -
        month = args[2]
        # -
        year = args[4]
        return Date_Text(day, month, year)

    def date_time(self, args):
        #DQUOTE
        day  = args[1]
        #-
        mon  = args[3]
        #-
        year = args[5]
        #SP
        time = args[7]
        #SP
        zone = args[9]
        #DQUOTE
        result = Date_Time(day, mon, year, time, zone)
        return result

    def date_year(self, args):
        return self.justConcatenateArgs(args)

    def date_month(self, args):
        return self.justConcatenateArgs(args)

    def delete(self, args):
        return SimpleCommandWithMailbox('DELETE', args[2])

    def digit_nz(self,args):
        return args[0]

    def done(self, args):
        return self.justConcatenateArgs(args)

    def envelope(self, args):
        #OPEN BRACKET
        date = args[1]
        #SP
        subject = args[3]
        #SP
        env_from = args[5]
        #SP
        sender = args[7]
        #SP
        reply_to = args[9]
        #SP
        to = args[11]
        #SP
        cc = args[13]
        #SP
        bcc = args[15]
        #SP
        in_reply_to = args[17]
        #SP
        message_id = args[19]
        #CLOSING BRACKET
        return Envelope(date, subject, env_from, sender, reply_to, to, cc, bcc, in_reply_to, message_id)

    def env_bcc(self, args):
        return self.convertAddressesOrNil(args)

    def env_cc(self, args):
        return self.convertAddressesOrNil(args)

    def env_date(self, args):
        return args[0]

    def env_from(self, args):
        return self.convertAddressesOrNil(args)

    def env_in_reply_to(self, args):
        return args[0]

    def env_message_id(self, args):
        return args[0]

    def env_reply_to(self, args):
        return self.convertAddressesOrNil(args)

    def env_sender(self, args):
        return self.convertAddressesOrNil(args)

    def env_subject(self, args):
        return args[0]

    def env_to(self, args):
        return self.convertAddressesOrNil(args)

    def examine(self, args):
        return SimpleCommandWithMailbox('EXAMINE', args[2])

    def fetch(self, args):
        text = None
        fetch_att = None
        fetch_att_list = None

        # FETCH
        # SP
        seq_set = args[2]
        # SP
        if len(args) == 5:
            if isinstance(args[4], Fetch_Att):
                fetch_att = args[4]
            else:
                text = args[4]
        else:
            fetch_att_list = []
            # OPENING BRACKET
            for i in range(5, len(args)-1, 2):
                fetch_att_list.append(args[i])
            # CLOSING BRACKET
        return Fetch(seq_set, text, fetch_att, fetch_att_list)

    def fetch_att(self, args):
        argcount = len(args)
        section = None
        partial = None

        text = str(args[0])
        if argcount >= 2:
            if isinstance(args[1], Section):
                section = args[1]
            else:
                text = text + str(args[1])
        elif argcount > 2:
            partial = '<' + str(args[3]) + '.' + str(args[5]) + '>'

        return Fetch_Att(text, section, partial)

    def flag(self, args):
        return args[0]

    def flag_extension(self, args):
        return self.justConcatenateArgs(args)

    def flag_fetch(self, args):
        return args[0]

    def flag_keyword(self, args):
        return args[0]

    def flag_list(self, args):
        # OPEN BRACKET
        flags = []
        if len(args) > 2:
            for i in range(1, len(args)-1):
                flags.append(args[i])
        # CLOSING BRACKET
        return Flag_List(flags)

    def flag_perm(self, args):
        return args[0]

    def greeting(self, args):
        # "*"
        # SP
        resp_cond = args[2]
        # CRLF
        return Greeting(resp_cond)

    def header_fld_name(self, args):
        return args[0]

    def header_list(self, args):
        # OPEN BRACKET
        headers = []
        if len(args) > 2:
            for i in range(1, len(args) - 1, 2):
                headers.append(args[i])
        # CLOSING BRACKET
        return Header_List(headers)

    def idle(self, args):
        return Idle()

    def list(self, args):
        return List(args[2], args[4])

    def list_char(self, args):
        return args[0]

    def list_mailbox(self, args):
        if len(args) == 1:  # string
            return args[0]
        else:  # 1*list_char
            return self.justConcatenateArgs(args)

    def list_wildcards(self, args):
        return str(args[0])

    def literal(self, args):
        # {
        length = args[1]
        # }
        # \r
        # \n
        text = ''
        for i in range(4, len(args)):
            text += str(args[i])
        result = Literal(length, text)
        return result

    def login(self, args):
        return Login(args[2], args[4])

    def lsub(self, args):
        return Lsub(args[2], args[4])

    def mailbox(self, args):
        return args[0]

    def mailbox_data(self, args):
        argcount = len(args)
        command = None
        flag_list = None
        mailbox_list = None
        nz_number_list = None
        mailbox = None
        status_att_list = None
        number = None

        if isinstance(args[0], int):
            number = args[0]
            # SP
            command = str(args[2])
        else:
            command = str(args[0]).upper()
            if command == 'FLAGS':
                # SP
                flag_list = args[2]
            elif command in ('LIST', 'LSUB'):
                # SP
                mailbox_list = args[2]
            elif command == 'SEARCH' and argcount > 1:
                nz_number_list = []
                for i in range(2, argcount, 2):
                    nz_number_list.append(args[i])
            elif command == 'STATUS':
                # SP
                mailbox = args[2]
                # SP
                # (
                if argcount > 7:
                    status_att_list = args[5]
                # )
        return Mailbox_Data(command, flag_list, mailbox_list, nz_number_list, mailbox, status_att_list, number)

    def mailbox_list(self, args):
        argcount = len(args)
        flags = None
        delimiter = None
        mailbox = None

        # "("
        if isinstance(args[1], Mbx_List_Flags):
            flags = args[1]
            # ")"
            # SP
            if args[4] != None:
                # DQUOTE
                delimiter = str(args[5])
                # DQUOTE
        else:
            if args[3] != None:
                # DQUOTE
                delimiter = str(args[4])
                # DQUOTE
        # SP
        mailbox = args[-1]

        return Mailbox_List(flags, delimiter, mailbox)

    def mbx_list_flags(self, args):
        flags = []
        for i in range(0, len(args), 2):
            flags.append(args[i])
        return Mbx_List_Flags(flags)

    def mbx_list_oflag(self, args):
        return str(args[0])

    def mbx_list_sflag(self, args):
        return str(args[0])

    def media_basic(self, args):
        if len(args) == 3:
            return Media_Basic(args[0], args[2])
        else:
            type = args[0] + args[1] + args[2]
            #SP
            media_subtype = args[4]
            return Media_Basic(type, media_subtype)

    def media_message(self, args):
        return '"MESSAGE" "RFC822"'

    def media_subtype(self, args):
        return args[0]

    def media_text(self, args):
        #DQUOTE
        #TEXT
        #DQUOTE
        #SP
        subtype = args[4]
        return Media_Text(subtype)

    def message_data(self, args):
        msg_att = None

        nz_number = args[0]
        # SP
        command = str(args[2]).upper()
        if command == 'FETCH':
            msg_att = args[4]
        return Message_Data(nz_number, command, msg_att)

    def msg_att(self, args):
        msg_att_list = []
        # (
        for i in range(1, len(args)-1, 2):
            msg_att_list.append(args[i])
        return Msg_Att(msg_att_list)

    def msg_att_static(self, args):
        argcount = len(args)

        attribute = str(args[0]).upper()
        envelope = None
        date_time = None
        nstring = None
        number = None
        body = None
        section = None
        uniqueid = None

        if attribute == 'ENVELOPE':
            envelope = args[2]
        elif attribute == 'INTERNALDATE':
            date_time = args[2]
        elif attribute == 'RFC822':
            if argcount == 4:
                attribute = attribute + str(args[1]).upper()
                nstring = args[3]
            else:
                nstring = args[2]
        elif attribute == 'RFC822.SIZE':
            number = args[2]
        elif attribute == 'BODY':
            if isinstance(args[1], Section):
                section = args[1]
                if argcount == 7:
                    # <
                    number = args[3]
                    # >
                # SP
                nstring = args[-1]
            else:
                if argcount == 4:
                    attribute = attribute + str(args[1]).upper()
                # SP
                body = args[-1]
        elif attribute == 'UID':
            uniqueid = args[2]

        return Msg_Att_Static(attribute, envelope, date_time, nstring, number, body, section, uniqueid)

    def msg_att_dynamic(self, args):
        flag_fetch_list = []
        # "FLAGS"
        # SP
        # (
        for i in range(3, len(args)-1, 2):
            flag_fetch_list.append(args[i])
        # )
        return Msg_Att_Dynamic(flag_fetch_list)

    def nil(self,args):
        return None

    def nstring(self, args):
        result = args[0]
        if args[0] == None:
            result = 'NIL'
        return result

    def number(self, args):
        return int(self.justConcatenateArgs(args))

    def nz_number(self,args):
        return int(self.justConcatenateArgs(args))

    def password(self, args):
        return args[0]

    def quoted(self, args):
        return self.justConcatenateArgs(args)

    def quoted_char(self, args):
        return self.justConcatenateArgs(args)

    def quoted_specials(self, args):
        return str(args[0])

    def rename(self, args):
        return Rename(args[2], args[4])

    def resp_cond_auth(self, args):
        cond = args[0]
        # SP
        text = args[2]
        return Resp_Cond_Auth(cond, text)

    def resp_cond_bye(self, args):
        # "BYE"
        # SP
        text = args[2]
        return Resp_Cond_Bye(text)

    def resp_cond_state(self, args):
        return Resp_Cond_State(str(args[0]).upper(), args[2])

    def resp_specials(self, args):
        return str(args[0])

    def resp_text(self, args):
        resp_text_code = None
        text = None
        if len(args) == 5: # [resp-text-code]
            resp_text_code = args[1]
            text = args[4]
        else: # nur text
            text = args[0]
        return Resp_Text(resp_text_code, text)

    def resp_text_code(self, args):
        argcount = len(args)
        code = None
        charset_list = None
        cap_data = None
        flag_perm_list = None
        nz_number = None
        other_text = None

        if isinstance(args[0], str):
            code = str(args[0]).upper()
        else:
            cap_data = args[0]

        if argcount != 1:
            if code == 'BADCHARSET':
                charset_list = []
                for i in range(3, argcount - 1, 2):
                    charset_list.append(args[i])
            elif code == 'PERMANENTFLAGS':
                flag_perm_list = []
                for i in range(3, argcount - 1, 2):
                    flag_perm_list.append(args[i])
            elif code in ('UIDNEXT', 'UIDVALIDITY', 'UNSEEN'):
                nz_number = args[2]
            else:
                other_text = self.justConcatenateArgs(args[2:])
        return Resp_Text_Code(code, charset_list, cap_data, flag_perm_list, nz_number, other_text)

    def response(self, args):
         list = []
         for element in args[:-1]:
             list.append(element)
         response_done = args[-1]
         return Response(list, response_done)

    def response_data(self, args):
        resp_cond_state = None
        resp_cond_bye = None
        mailbox_data = None
        message_data = None
        capability_data = None

        if isinstance(args[2], Resp_Cond_State):
            resp_cond_state = args[2]
        elif isinstance(args[2], Resp_Cond_Bye):
            resp_cond_bye = args[2]
        elif isinstance(args[2], Mailbox_Data):
            mailbox_data = args[2]
        elif isinstance(args[2], Message_Data):
            message_data = args[2]
        elif isinstance(args[2], Capability_Data):
            capability_data = args[2]

        return Response_Data(resp_cond_state, resp_cond_bye, mailbox_data, message_data, capability_data)

    def response_done(self, args):
        return args[0]

    def response_fatal(self, args):
        return Response_Fatal(args[2])

    def response_tagged(self, args):
        return Response_Tagged(args[0], args[2])

    def response_untagged(self, args):
        list = []
        for element in args:
            list.append(element)
        return Response_Untagged(list)

    def search(self, args):
        charset = None
        search_key_list = []
        index = 2
        if args[2] == 'CHARSET':
            charset = args[4]
            index = 6
        for i in range(index, len(args), 2):
            search_key_list.append(args[i])
        return Search(charset, search_key_list)

    def search_key(self, args):
        if len(args) == 1:
            return Search_Key(str(args[0]), argument=None)
        else:
            # Dieser Zweig behandelt die letzte Option nicht richtig! "(" search_key (SP search_key)* ")"
            return Search_Key(str(args[0]), argument=self.justConcatenateArgs(args[1:]))

    def section(self, args):
        section_spec = None
        if len(args) == 3:
            section_spec = args[1]
        return Section(section_spec)

    def section_msgtext(self, args):
        argcount = len(args)
        text = str(args[0])
        header_list = None
        if argcount == 3:
            header_list = args[2]
        elif argcount == 4:
            text = text + str(args[1])
            header_list = args[3]
        return Section_Msgtext(text, header_list)

    def section_part(self, args):
        return self.justConcatenateArgs(args)

    def section_spec(self, args):
        msg = None
        part = None
        text = None
        if isinstance(args[0], Section_Msgtext):
            msg = args[0]
        else:
            part = args[0]
            if len(args) == 3:
                text = args[2]
        return Section_Spec(msg, part, text)

    def section_text(self, args):
        if isinstance(args[0], Section_Msgtext):
            return Section_Text(args[0], None)
        else:
            return Section_Text(None, args[0])

    def select(self, args):
        return SimpleCommandWithMailbox('SELECT', args[2])

    def seq_number(self, args):
        return str(args[0])

    def seq_range(self, args):
        return self.justConcatenateArgs(args)

    def sequence_set(self, args):
        return self.justConcatenateArgs(args)

    def status(self, args):
        # "STATUS"
        # SP
        mailbox = args[2]
        # SP
        # OPENING BRACKET
        list = []
        for i in range(5, len(args)-1, 2):
            list.append(args[i])
        #CLOSING BRACKET
        return Status(mailbox, list)

    def status_att(self, args):
        return str(args[0])

    def status_att_list(self, args):
        list = []
        for i in range(0, len(args), 2):
            list.append(args[i])
        return Status_Att_List(list)

    def status_att_val(self, args):
        return Status_Att_Val(str(args[0]).upper(), args[2])

    def store(self, args):
        return Store(args[2], args[4])

    def store_att_flags(self, args):
        return self.justConcatenateArgs(args)

    def string(self, args):
        #print(args[0])
        return args[0]

    def subscribe(self, args):
        return SimpleCommandWithMailbox('SUBSCRIBE', args[2])

    def tag(self, args):
        return self.justConcatenateArgs(args)

    def text(self, args):
        return self.justConcatenateArgs(args)

    def time(self, args):
        return self.justConcatenateArgs(args)

    def uid(self, args):
        return UID(args[2])

    def uniqueid(self, args):
        return args[0]

    def unsubscribe(self, args):
        return SimpleCommandWithMailbox('UNSUBSCRIBE', args[2])

    def userid(self, args):
        return args[0]

    def zone(self, args):
        return self.justConcatenateArgs(args)

    def x_command(self, args):
        return None

    def justConcatenateArgs(self, args):
        result = ""
        for i in args:
            result = result + str(i)
        return result

    def convertAddressesOrNil(self, args):
        if len(args) == 1: #None
            return 'NIL'
        else:
            #OPEN BRACKET
            addresses = []
            for i in range(1, len(args)-1):
                addresses.append(args[i])
            #CLOSING BRACKET
            return Env_List(addresses)
