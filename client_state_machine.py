import time
def replace_emojis_with_code(string, emoji_dict1):
    for emoji, code in emoji_dict1.items():
        string = string.replace(emoji, code)
    return string

"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *

def ensure_utf8(string):
    if isinstance(string, str):
        return string.encode('utf-8').decode('utf-8')
    return string
import json

PROTOCOL = 7

class ClientSM:
    def __init__(self, s):

        self.emoji_dict = {
                    "😊": "\U0001F60A",
                    "😀": "\U0001F600",
                    "🥲": "\U0001F972",
                    "😎": "\U0001F60E",
                    "😍": "\U0001F60D",
                    "👍": "\U0001F44D",
                    "👎": "\U0001F44E",
                    "🔥": "\U0001F525",
                    "🤔": "\U0001F914",
                    "💩": "\U0001F4A9",
                    "🙄": "\U0001F644",
                    "🎉": "\U0001F389",
                    "👏": "\U0001F44F",
                    "💪": "\U0001F4AA"
                }
        self.emoji_dict1 = {
                    "happy_face": "\U0001F60A",
                    "grinning_face": "\U0001F600",
                    "smiling_face_with_tear": "\U0001F972",
                    "smiling_face_with_sunglasses": "\U0001F60E",
                    "smiling_face_with_heart_eyes": "\U0001F60D",
                    "thumbs_up": "\U0001F44D",
                    "thumbs_down": "\U0001F44E",
                    "fire": "\U0001F525",
                    "thinking_face": "\U0001F914",
                    "pile_of_poo": "\U0001F4A9",
                    "face_with_rolling_eyes": "\U0001F644",
                    "party_popper": "\U0001F389",
                    "clapping_hands": "\U0001F44F",
                    "flexed_biceps": "\U0001F4AA"
                }

        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.history = []



    def encrypt_unicode(self, string):
        # Encrypting a UTF-8 string (including emojis) using a simple cipher
        encrypted = ''
        for char in string:
            # Simple cipher: rotate each unicode code point
            encrypted += chr((ord(char) + PROTOCOL) % 0x110000)  # Unicode range
        return encrypted



    def decrypt_unicode(self, string):
        # Decrypting a UTF-8 string (including emojis) using a simple cipher
        decrypted = ''
        for char in string:
            # Simple cipher: reverse rotate each unicode code point
            decrypted += chr((ord(char) - PROTOCOL) % 0x110000)  # Unicode range
        return decrypted
        

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''
    def update_out_msg_with_history(self):
        
        history_str = ""
        for message in self.history:
            history_str += message + "\n"
        ctime = time.strftime('%H:%M', time.localtime())
        self.out_msg = f'[{ctime}]'+'\n'+history_str + self.out_msg
        self.history = []
    
    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    my_msg = replace_emojis_with_code(my_msg, self.emoji_dict)
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    my_msg = replace_emojis_with_code(my_msg, self.emoji_dict)
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    my_msg = replace_emojis_with_code(my_msg, self.emoji_dict)
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    my_msg = replace_emojis_with_code(my_msg, self.emoji_dict)
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    pass
                    # self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                temp = my_msg
                temp1 = replace_emojis_with_code(temp,self.emoji_dict1)
                #历史功能
                self.history.append("[" + self.me + "]" + temp1) 
                my_msg = self.encrypt_unicode(my_msg)
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                # Removed the calculate_sum check

                    self.out_msg += "A Server Error Occured! Please Try Again!"
                else:
                    rec = self.decrypt_unicode(peer_msg["message"])
                    rec1 = replace_emojis_with_code(rec,self.emoji_dict1)
                    self.out_msg += peer_msg["from"] + rec1


            # Display the menu again
            # if self.state == S_LOGGEDIN:
            #     self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        self.update_out_msg_with_history()
        print(self.out_msg)
        return self.out_msg
