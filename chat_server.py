"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import emoji
import random

# import subprocess
# import client_state_machine as sm
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
# sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 60 * 1000, 30 * 1000))

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        # self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        # self.sonnet = pkl.load(self.sonnet_f)
        # self.sonnet_f.close()
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        #a dict to store the trgistered names
        self.users=dict()
        #a dict to store the emojis
        self.last_msg=None
       

        #set for secure message
        self.base=6
        self.clock=11
        self.snakescore = {}
        self.sokobanscore = {}
        #integrate emoji
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

    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    # # integrate emoji
    def convert_emoji(self,message):
        for (word,unicode) in self.emoji_dict.items():
           message=message.replace(word,unicode)
        return message

    def login(self, sock):
        #read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            print("login:", msg)
            if len(msg) > 0:
                ##integrate the password to the login part##

                if msg["action"] == "login":
                    name = msg["name"]
                    password = msg['password']
                    if name not in self.users.keys():
                        mysend(sock,json.dumps(
                            {'action':'login','status':'notregister'}))
                    elif self.group.is_member(name) == True:
                        mysend(sock,json.dumps(
                            {'action':'login','status':'duplicate'}))
                    elif self.group.is_member(name) != True:
                        #check whether the name-password pair is correct
                        if self.users[name] == password:
                        #move socket from new clients list to logged clients
                            self.new_clients.remove(sock)
                        #add into the name to sock mapping
                            self.logged_name2sock[name] = sock
                            self.logged_sock2name[sock] = name
                        #load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name]=pkl.load(open(name+'.idx','rb'))
                            except IOError: #chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps({"action":"login", "status":"ok"}))
                    else: #a client under this name has already logged in
                        mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
                        print(name + ' duplicate login attempt')
                elif msg['action'] == 'register':
                    name = msg['name']
                    password = msg['password']
                    print(name,password)
                    if name in self.users.keys():
                        mysend(sock,json.dumps(
                            {'action':'register','status':'duplicate'}))
                    else:
                        self.users[name]=password
                        mysend(sock,json.dumps(
                            {'action':'register','status':'ok'}))
                else:
                    print ('wrong code received')
            else: #client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

    def record_history(self,msg):
        self.last_msg=msg

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code
        msg = myrecv(from_sock)
        msg = json.loads(msg)
        #integrate the emoji part
        # msg=self.convert_emoji(msg)
        if len(msg) > 0:
#==============================================================================
# handle connect request
#==============================================================================
            #set for secure message
            if msg["action"]=="produce_public_private":
                from_name=self.logged_sock2name[from_sock]
                to_name=msg["target"]
                to_sock=self.logged_name2sock[to_name]
                mysend(to_sock, json.dumps(
                        {"action": "produce_public_private", 
                        "target": from_name, "from": from_name,"message":msg["message"]}))
            elif msg["action"]=="produce_shared_keys":
                from_name=self.logged_sock2name[from_sock]
                to_name=msg["target"]
                to_sock=self.logged_name2sock[to_name]
                mysend(to_sock, json.dumps(
                        {"action": "produce_shared_keys", 
                        "target": from_name, "from": from_name,"message":msg["message"]}))
            
           
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action":"connect", "status":"self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action":"connect", "status":"success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
                else:
                    msg = json.dumps({"action":"connect", "status":"no-user"})
                mysend(from_sock, msg)
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
            elif msg["action"] == "exchange":
                #reliable message
                self.record_history(msg)
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                said = msg["from"]+msg["message"]
                # said2 = text_proc(msg["message"], from_name)
                said2=msg['message']
                # print(said2)
                self.indices[from_name].add_msg_and_index(said2)
                #emulate a bad server'
                binary_string = ''.join(format(ord(char), '08b') for char in msg["message"][:-1])
                # Generate a random indices to flip
                bit_index_1 = random.randint(0, len(binary_string)-1)
                

            
                binary_list = [int(bit) for bit in binary_string]

                # Flip the bits at the two indices
                binary_list[bit_index_1] = 1 - int(binary_string[bit_index_1])
                
                modified_binary_string = ''.join(str(bit) for bit in binary_list)
                unreliable_msg = ''
                for i in range(0, len(modified_binary_string), 8):
                    byte = modified_binary_string[i:i+8]
                    char = chr(int(byte, 2))
                    unreliable_msg += char
                unreliable_msg=unreliable_msg+msg["message"][-1]

                
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"],
                                                 "message":self.convert_emoji(msg['message'])}))
            
            #detect the error and resend
            # elif msg["action"] == "correct":
            #     from_name = self.logged_sock2name[from_sock]
            #     to_sock = self.logged_name2sock[from_name]
               

            #     # unreliable_msg=''
               
            #     # print(self.last_msg)
            #     # for thing in self.last_msg["message"][:-1]:
            #     #     print(thing)
            #     #     mark=ord(thing)
            #     #     new_msg=chr(mark)
            #     #     print(new_msg)
            #     #     unreliable_msg+=new_msg
                    
            #     # self.last_msg["message"]=unreliable_msg+self.last_msg["message"][-1]
                
            #     mysend(to_sock, json.dumps({"action":"exchange", "from":self.last_msg["from"], "message":self.convert_emoji(self.last_msg['message'])}))
            #     # 
            #     # 
                # to transfer the result of online games
            elif msg['action']=='trans_game':
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                said = msg["from"]+msg["message"] 
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"trans_game", "from":msg["from"], "message": self.convert_emoji(msg['message'])}))

#==============================================================================
#                 listing available peers
#==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                print('here:\n', poem)
                mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps({"action":"time", "results":ctime}))


            elif msg["action"] == "weather":
                import requests
                base_url = "http://api.openweathermap.org/data/2.5/weather?"
                city_name = msg["city"]
                complete_url = base_url + "appid=" + api_key + "&q=" + city_name
                response = requests.get(complete_url)
                weather_data = response.json()
                if weather_data["cod"] != "404":
                    main_data = weather_data["main"]
                    temperature = main_data["temp"]
                    pressure = main_data["pressure"]
                    humidity = main_data["humidity"]
                    weather_description = weather_data["weather"][0]["description"]
                    # Format the weather information as needed
                    out = f"Temperature: {temperature} K\nPressure: {pressure} hPa\nHumidity: {humidity}%\nDescription: {weather_description}"
                    mysend(from_sock, json.dumps({"action":"weather", "results":out}))

#==============================================================================
#                 search
#==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                # search_rslt = (self.indices[from_name].search(term))
                search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
                print('server side search: ' + search_rslt)
                mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action":"disconnect"}))
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================

        else:
            #client died unexpectedly
            self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)

def main():
    server=Server()
    server.run()

main()
