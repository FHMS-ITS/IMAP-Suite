#!/usr/bin/python3

from statemachine import StateMachine, State
from utils.imap_constants import *

class ImapMachine(StateMachine):

    #States
    wait_for_greeting = State(WAIT_FOR_GREETING, initial=True)
    not_auth = State(NOT_AUTH)
    auth_check = State(AUTH_CHECK)
    auth = State(AUTH)
    selected = State(SELECTED)
    selected_pending = State(SELECTED_PENDING)
    idle_auth = State(IDLE_AUTH)
    idle_selected = State(IDLE_SELECTED)
    disconnected = State(DISCONNECTED)

    #Login-States
    auth_wait_for_cont_req = State(AUTH_WAIT_FOR_CONT_REQ)
    auth_wait_for_base64 = State(AUTH_WAIT_FOR_BASE64)

    #Transitions from wait_for_greeting
    greeting = wait_for_greeting.to(not_auth)
    preauth = wait_for_greeting.to(auth)

    #Transitions from not_auth
    auth_plain = not_auth.to(auth_wait_for_cont_req)
    auth_login = not_auth.to(auth_check)

    #Transitions Auth PLAIN
    auth_con_req = auth_wait_for_cont_req.to(auth_wait_for_base64)
    auth_base64 = auth_wait_for_base64.to(auth_check)

    #Transitions from auth_check
    auth_ok = auth_check.to(auth)
    auth_no = auth_check.to(not_auth)

    #Transitions from auth
    select_examine = auth.to(selected_pending)
    auth_idle = auth.to(idle_auth)

    #Transitions from selected_pending
    select_examine_ok = selected_pending.to(selected)
    select_examine_no = selected_pending.to(auth)

    #Transitions from selected
    close = selected.to(auth)
    logout = selected.to(disconnected)
    selected_idle = selected.to(idle_selected)

    #Transitions from idle_auth
    idle_auth_done = idle_auth.to(auth)

    #Transitions from idle_selected
    idle_selected_done = idle_selected.to(selected)

    #Transitions to disconnected
    disconnect_wfg = wait_for_greeting.to(disconnected)
    disconnect_na = not_auth.to(disconnected)
    disconnect_ac = auth_check.to(disconnected)
    disconnect_a = auth.to(disconnected)
    disconnect_awfcr = auth_wait_for_cont_req.to(disconnected)
    disconnect_awfb = auth_wait_for_base64.to(disconnected)
    disconnect_sp = selected_pending.to(disconnected)
    disconnect_s = selected.to(disconnected)
    disconnect_ia = idle_auth.to(disconnected)
    disconnect_is = idle_selected.to(disconnected)
    disconnect_d = disconnected.to(disconnected)

    def getDisconnectTransition(self, state):
        if state == WAIT_FOR_GREETING:
            return self.disconnect_wfg
        elif state == NOT_AUTH:
            return self.disconnect_na
        elif state == AUTH_CHECK:
            return self.disconnect_ac
        elif state == AUTH:
            return self.disconnect_a
        elif state == AUTH_WAIT_FOR_CONT_REQ:
            return self.disconnect_awfcr
        elif state == AUTH_WAIT_FOR_BASE64:
            return self.disconnect_awfb
        elif state == SELECTED_PENDING:
            return self.disconnect_sp
        elif state == SELECTED:
            return self.disconnect_s
        elif state == IDLE_AUTH:
            return self.disconnect_ia
        elif state == IDLE_SELECTED:
            return self.disconnect_is
        elif state == DISCONNECTED:
            return self.disconnect_d

    def getIdleTransition(self, state):
        if state == AUTH:
            return self.auth_idle
        elif state == SELECTED:
            return self.selected_idle

    def getIdleDoneTransition(self, state):
        if state == IDLE_AUTH:
            return self.idle_auth_done
        elif state == IDLE_SELECTED:
            return self.idle_selected_done
