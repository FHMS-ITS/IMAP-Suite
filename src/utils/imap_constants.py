#Encoding
ENCODING = 'latin1'

# States für Statemachine
WAIT_FOR_GREETING = 'wait_for_greeting'
NOT_AUTH = 'not_auth'
AUTH_CHECK = 'auth_check'
AUTH = 'auth'
AUTH_WAIT_FOR_CONT_REQ = 'auth_wait_for_cont_req'
AUTH_WAIT_FOR_BASE64 = 'auth_wait_for_base64'
SELECTED = 'selected'
SELECTED_PENDING = 'selected_pending'
IDLE_AUTH = 'idle_auth'
IDLE_SELECTED = 'idle_selected'
DISCONNECTED = 'disconnected'

# Hardcoded Responses
UNKNOWN_COMMAND_RESPONSE = '* BAD Proxy: Unknown command\r\n'

# Response Conditions
COND_OK = 'OK'
COND_NO = 'NO'
COND_BYE = 'BYE'

#Suppoorted Starting Rules for Parsing
PARSING_STARTING_RULES = {'command', 'response', 'response_untagged', 'greeting', 'done'}

#QTreeWidget Strings
QTREE_REST = 'rest'
QTREE_SP = 'SP'
QTREE_CR = 'CR'
QTREE_LF = 'LF'
QTREE_CRLF = 'CRLF'
QTREE_TOKEN = 'TOKEN'
QTREE_CHAR8STAR = 'CHAR8*'

