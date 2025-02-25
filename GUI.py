#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import StringVar
from tkinter import messagebox
from chat_utils import *
from tkinter import Frame
from PIL import Image
import json
import pickle
from PIL import ImageTk, Image
import random
import pygame
import speech_recognition as sr
import time
import requests
from client_state_machine import ClientSM

# to apply the musicplayer as another path
# import subprocess

user_dict={}
# GUI class for the chat
class GUI:
    
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        # Frame.__init__(self, send, recv, sm, s)
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
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

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width = False, height = False)
        self.login.configure(width = 400, height = 300)  # Adjusted size
        # Load the title image
        self.title_image = PhotoImage(file="title.PNG")
        self.title_image = self.title_image.subsample(4, 4)

        # Create a label for the title image
        self.title_label = Label(self.login, image=self.title_image)

        # Place the title image label at the top of the window
        self.title_label.place(relx=0.5, rely=0.18, anchor='center')
        # Load icons
        self.user_icon = PhotoImage(file="user_icon.png")
        self.user_icon = self.user_icon.subsample(12, 12)  # Scaled down to half size

        self.password_icon = PhotoImage(file="password_icon.png")
        self.password_icon = self.password_icon.subsample(12, 12)  # Scaled down to half size

        # Create Labels for icons
        self.user_icon_label = Label(self.login, image=self.user_icon)
        self.password_icon_label = Label(self.login, image=self.password_icon)

        # Place icon labels parallel with the labels
        self.user_icon_label.place(relx=0.1, rely=0.35)  # Adjusted position
        self.password_icon_label.place(relx=0.1, rely=0.55)  # Adjusted position

        # create a Label
        self.labelName = Label(self.login, text = "Name: ", font = "Helvetica 14 bold")
        self.labelName.place(relheight = 0.2, relx = 0.2, rely = 0.3)

        # create a Label for password
        self.Pwd = Label(self.login, text="Password: ", font="Helvetica 14 bold")
        self.Pwd.place(relheight = 0.2, relx = 0.2, rely = 0.5)

        # create an entry box for typing the message
        self.entryName = Entry(self.login, font = "Helvetica 10")
        self.entryName.place(relwidth = 0.4, relheight = 0.1, relx = 0.4, rely = 0.35)

        # a entry box for password
        self.entryPwd = Entry(self.login, font = "Helvetica 10", show='*')
        self.entryPwd.place(relwidth = 0.4, relheight = 0.1, relx = 0.4, rely = 0.55)

        # set the focus of the cursor
        self.entryName.focus()

        # Login button
        self.go = Button(self.login, text = "  LOGIN  ", font = "Helvetica 14 bold", bg = "#80c1ff", relief = RAISED, activebackground = "#ADD8E6",
                        command = lambda: self.goAhead(self.entryName.get(),self.entryPwd.get()))
        self.go.place(relx = 0.2, rely = 0.75)  # Adjusted position, width and height

        # Register button
        self.account = Button(self.login, text = "REGISTER", font = "Helvetica 14 bold", bg = "#80c1ff", relief = RAISED, activebackground = "#ADD8E6",
                            command = lambda: self.signup())
        self.account.place(relx = 0.5, rely = 0.75)  # Adjusted position, width and height

        self.Window.mainloop()

    def signup(self):
        # sign up window
        self.signup = Toplevel()
        self.signup.title("Sign up")
        self.signup.resizable(width = False, height = False)
        self.signup.configure(width = 400, height = 300)  # same background as login window

        # create a Label
        self.pls2 = Label(self.signup, text = "Please create an account", justify = CENTER, font = "Helvetica 20 bold")  
        self.pls2.place(relheight = 0.15, relx = 0.2, rely = 0.07)

        # User name Label
        self.labelName2 = Label(self.signup, text = "Name: ", font = "Helvetica 14 bold")  
        self.labelName2.place(relheight = 0.2, relx = 0.15, rely = 0.2)

        # Password Label
        self.Pwd2 = Label(self.signup, text="Password: ", font="Helvetica 14 bold")
        self.Pwd2.place(relheight = 0.2, relx = 0.15, rely = 0.4)

        # Confirm password Label
        self.confirmPwd2 = Label(self.signup, text="Confirm : ", font="Helvetica 14 bold")
        self.confirmPwd2.place(relheight = 0.2, relx = 0.15, rely = 0.6)

        # User name Entry
        self.entryName2 = Entry(self.signup, font = "Helvetica 14")
        self.entryName2.place(relwidth = 0.4, relheight = 0.1, relx = 0.4, rely = 0.25)

        # Password Entry
        self.entryPwd2 = Entry(self.signup, font = "Helvetica 14", show='*')
        self.entryPwd2.place(relwidth = 0.4, relheight = 0.1, relx = 0.4, rely = 0.45)

        # Confirm password Entry
        self.entryconfirmPwd2 = Entry(self.signup, font = "Helvetica 14", show='*')
        self.entryconfirmPwd2.place(relwidth = 0.4, relheight = 0.1, relx = 0.4, rely = 0.65)

        # set the focus of the cursor
        self.entryName2.focus()

        # Create Account button
        self.BackToLogin = Button(self.signup, text = "Create Account", font = "Helvetica 14 bold", command = lambda: self.creataccount(self.entryName2.get(),self.entryPwd2.get(),self.entryconfirmPwd2.get()))
        self.BackToLogin.place(relx = 0.5, rely = 0.85, anchor='center')  # centered button

        self.Window.mainloop()


  
    def goAhead(self, name,pwd):
        if len(name) > 0:
            # msg = json.dumps({"action":"login", "name": name})
            # integrate the pwd
            msg = json.dumps({"action": "login", "name": name,'password':pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state = NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")   
                self.textCons.insert(END, menu +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)

            #wrong name
            elif response['status'] == 'notregister':
                messagebox.showerror(
                    title='Error',message='User name does not exist.')
            #wrong password
            elif response['status'] == 'wrongpassword':
                messagebox.showerror(
                    title='Error',message='User name or password is wrong.')
            elif response['status'] == 'duplicate':
                messagebox.showerror(
                    title='Error',message='You already logged in.')
                # while True:
                #     self.proc()
        # the thread to receive messages
            process = threading.Thread(target=self.proc)
            process.daemon = True
            process.start()

    
        
    def creataccount(self,name,pwd,confirmpwd):
        if name == '' or pwd == '' or confirmpwd=='':
            messagebox.showwarning(
                title='Invalid input', message='User name or password is empty')
            #return
        if pwd !=confirmpwd:
            messagebox.showwarning(
                title='Password not correct', message='Please confirm password again')
        else:
            msg = json.dumps({'action':'register','name':name,'password':pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response['status'] == 'ok':
                messagebox.showinfo('Success','You have successfully created an account!')
                self.signup.destroy()
  
    # The main layout of the chat
    def layout(self,name):
        
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 470,
                              height = 550,
                              bg = "#17202A")
        self.labelHead = Label(self.Window,
                             bg = "#17202A", 
                              fg = "#EAECEE",
                              text = self.name ,
                               font = "Helvetica 13 bold",
                               pady = 5)
          
        self.labelHead.place(relwidth = 1)
        self.line = Label(self.Window,
                          width = 450,
                          bg = "#ABB2B9")
          
        self.line.place(relwidth = 1,
                        rely = 0.07,
                        relheight = 0.012)
          
        self.textCons = Text(self.Window,
                             width = 20, 
                             height = 2,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = "Helvetica 14", 
                             padx = 5,
                             pady = 5)
          
        self.textCons.place(relheight = 0.745,
                            relwidth = 1, 
                            rely = 0.08)
          
        self.labelBottom = Label(self.Window,
                                 bg = "#ABB2B9",
                                 height = 80)
          
        self.labelBottom.place(relwidth = 1,
                               rely = 0.8)
          
        self.entryMsg = Entry(self.labelBottom,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = "Helvetica 13")
          
        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth = 0.77,
                        relheight = 0.03,
                        rely = 0.008,
                        relx = 0.008)
    
          
        self.entryMsg.focus()
          
        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 12 bold", 
                                width = 20,
                                command = lambda : self.sendButton(self.entryMsg.get()))
          
        self.buttonMsg.place(relx = 0.792,
                         rely = 0.008,
                         relheight = 0.03, 
                         relwidth = 0.181)
          
        self.textCons.config(cursor = "arrow")

        #Create a time button
        self.buttonTime = Button(self.Window, text="WELCOME", font="Helvetica 12 bold", width=20, command=lambda: self.show_instructions())
        self.buttonTime.place(relx=0.01, rely=0.91, relwidth=0.18, relheight=0.07)

        self.buttonUserList = Button(self.Window, text="WEATHER", font="Helvetica 12 bold", width=20, command=lambda: self.weatherButton())
        self.buttonUserList.place(relx=0.205, rely=0.91, relwidth=0.18, relheight=0.07)

        self.buttonPoem = Button(self.Window, text="Polish", font="Helvetica 12 bold", width=20, command=lambda: self.polishButton())
        self.buttonPoem.place(relx=0.4, rely=0.91, relwidth=0.18, relheight=0.07)

        self.buttonEmoji = Button(self.Window, text="EMOJI", font="Helvetica 12 bold", width=20, command=lambda: self.open_emoji_window())
        self.buttonEmoji.place(relx=0.595, rely=0.91, relwidth=0.18, relheight=0.07)

        self.buttonGame = Button(self.Window, text="VOICE", font="Helvetica 12 bold", width=20, command=lambda: self.recognize_speech())
        self.buttonGame.place(relx=0.79, rely=0.91, relwidth=0.18, relheight=0.07)
        
          
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
          
        # place the scroll bar 
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
          
        scrollbar.config(command = self.textCons.yview)
          
        self.textCons.config(state = DISABLED)
  
    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)

    #function to get the time 
    def timeButton(self):
        self.textCons.config(state = DISABLED)
        self.my_msg='time'

    def weatherButton(self):
        self.textCons.config(state = DISABLED)
        self.my_msg='weather'
    #function to generate the UserList
    def UserListButton(self):
        self.textCons.config(state = DISABLED)
        self.my_msg='who'
    

    #function to get a random poem
    def PoemButton(self):
        n=random.randint(1,109)
        self.textCons.config(state = DISABLED)
        self.my_msg=f'p{n}'
    
    def instructions(self):
        self.textCons.insert(END, menu +"\n\n")      
        self.textCons.config(state = DISABLED)
        self.textCons.see(END)
    
    #emoji window
    def open_emoji_window(self):
        # 创建一个新的窗口
        self.emoji_window = Toplevel()
        self.emoji_window.resizable(width = False, 
                                        height = False)
        self.emoji_window.configure(width = 400,
                                        height = 300)
        self.emoji_window.title("Select an Emoji")

        # 创建一个字典，键是emoji的名字，值是emoji的代码
        self.emoji_dict = {
                    "😊": "happy_face",
                    "😀": "grinning_face",
                    "🥲": "smiling_face_with_tear",
                    "😎": "smiling_face_with_sunglasses",
                    "😍": "smiling_face_with_heart_eyes",
                    "👍": "thumbs_up",
                    "👎": "thumbs_down",
                    "🔥": "fire",
                    "🤔": "thinking_face",
                    "💩": "pile_of_poo",
                    "🙄": "face_with_rolling_eyes",
                    "🎉": "party_popper",
                    "👏": "clapping_hands",
                    "💪": "flexed_biceps"
                }

        # 创建emoji选择按钮
        for emoji_name, emoji_code in self.emoji_dict.items():
            emoji_button = Button(self.emoji_window, text=emoji_name, command=lambda e=emoji_code: self.insert_emoji(e))
            emoji_button.pack()
    def insert_emoji(self, emoji):
        self.entryMsg.insert(END, emoji)
        self.emoji_window.destroy()
    
    def show_instructions(self):
        # 指令窗口
        self.instructions_window = Toplevel()
        self.instructions_window.title("Instructions")
        self.instructions_window.resizable(width=False, height=False)
        self.instructions_window.configure(width = 370,
                              height = 250,
                              bg = "#17202A")

        # Userlist button
        self.btn_userlist = Button(self.instructions_window, text="who: to find out who else are there", font="Helvetica 14", width=60)
        self.btn_userlist.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.18)

        # Connect button
        self.btn_connect = Button(self.instructions_window, text="c _peer_: to connect to the _peer_", font="Helvetica 14", width=60)
        self.btn_connect.place(relx=0.02, rely=0.22, relwidth=0.96, relheight=0.18)

        # Poem button
        self.btn_poem = Button(self.instructions_window, text="? _term_: to search your chat logs", font="Helvetica 14", width=60)
        self.btn_poem.place(relx=0.02, rely=0.42, relwidth=0.96, relheight=0.18)

        self.btn_2 = Button(self.instructions_window, text="p _#_: to get number <#> sonnet", font="Helvetica 14", width=60)
        self.btn_2.place(relx=0.02, rely=0.62, relwidth=0.96, relheight=0.18)
        # Close button
        self.btn_close = Button(self.instructions_window, text="Close", font="Helvetica 14", width=20, command=self.instructions_window.destroy)
        self.btn_close.place(relx=0.68, rely=0.82, relwidth=0.30, relheight=0.16)

    def recognize_speech(self):
    # Initialize recognizer
        r = sr.Recognizer()

        # Capture audio from microphone
        with sr.Microphone() as source:
            audio_data = r.listen(source)
            try:
                # Convert speech to text
                text = r.recognize_google(audio_data)
                # text_entry.delete(0, tk.END)
                self.entryMsg.insert(END, text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

    #function to quit
    def quitButton(self):
        self.textCons.config(state = DISABLED)
        self.my_msg='q'

    def replace_emojis_with_code(self, string, emoji_dict1):
        for emoji, code in emoji_dict1.items():
            string = string.replace(emoji, code)
        return string
    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg += self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state = NORMAL)
                self.textCons.insert(END, self.system_msg +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)
                self.system_msg=''
    
    def polishButton(self):
        text_msg = self.entryMsg.get()
        polished = self.polish_with_chatgpt(text_msg)
        messagebox.showinfo("Message Polished", polished)

    def run(self):
        self.login()

# create a GUI class object
if __name__ == "__main__": 
    g = GUI("","","","")
