'''
Author:     OCybress
Date:       01-02-2024
Summary:    A server manager for the video game Path of Titans.
Updates:    01/08/2024  Moved App class to its own module.
                        Cleaned up App class.
                        Added get_external_ip function.
                        Added get_internal_ip function.
            01/09/2024  message box scroll by now auto scrolls with messages.
                        thread_factory is working, need to migrate the rest of the 
                            threads to use thread factory.
                        added exit button to allow for proper program termination.

                        
       
            
'''
import os
import sys
from pathlib import Path
import requests
from datetime import datetime
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter.tix import *
from tkinter import Text, Scrollbar, StringVar, filedialog
import uuid
import configparser as cp
import threading
import socket
import log
from err import error

'TODO: Setup versioning..'

appGUUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'
AlderonGamesCMDURL = 'https://launcher-cdn.alderongames.com/AlderonGamesCmd-Win64.exe'
GuuidRequestUrl = 'https://duckduckgo.com/?q=random+guid&atb=v296-1&ia=answer'
tokenFromFile = True
serverExeLocation = '/PathOfTitans/Binaries/Win64/PathOfTitansServer-Win64-Shipping.exe'

class App:
    def __init__(self, root, tt, thread_factory):
        '''
        lists of names and display text for buttons, labels, etc.
        '''
        self.labelList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir', 'Database', 'Branch', 'Map']
        self.labelText = ['Server Name', 'Auth Token', 'Port', 'GUUID', 'Install Dir', 'Database', 'Branch', 'Map']
        self.entryList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir']
        self.buttonList = ['StartServer','StopServer','UpdateServer']
        self.buttonText = ['Start Server','Stop Server','Update Server']

        self.yStart = 20
        self.yStep = 30
        self.xStart = 20
        self.entryXStart = 120
        self.labelWidth = 70
        self.labelHeight = 25
        self.labelJustify = 'left'
        self.labelForgroundColor = "#333333"
        self.entryWidth = 128
        self.entryHeight = 25
        self.entryJustify = 'left'
        self.entryForgroundColor = "#333333"

        '''
        {LabelName:{objects: [tkinterLabel, [tkinkerEntry|button|message]}}
        '''
        self.componentDict = {}

        self.thread_factory = thread_factory
        self.threads = {}
        self.create_gui(root, tt)

    def get_value(self, entry):
        '''
        get a value stored in a tk object
        '''
        return entry.get()

    def get_external_ip(self):
        try:
            response = requests.get("https://httpbin.org/ip")
            if response.status_code == 200:
                external_ip = response.json().get("origin")
                return external_ip
            else:
                return "Unable to fetch external IP"
        except Exception as e:
            return f'Error: {e}'

    def get_internal_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception as e:
            return f'Error: {e}'

    def update_message(self, var, nl=True):
        '''
        Updates the message box in the bottom of the program.

        Parameters:
        - var: The message to be displayed.
        - nl: Boolean flag to indicate whether to add a newline.

        Returns:
        - None
        '''
        message_time = str(datetime.now())[:19]
        formatted_message = f'\n{message_time} - {var}' if nl else f'{var}'

        self.message.insert(tk.END, formatted_message)
        log.write(formatted_message, debug=True)

        self.message.yview_moveto(1.0)

    def get_install_dir(self):
        '''
        When the user clicks the directory icon this function
        asks them where they would like to install.
        '''
        self.update_message(f'Getting install dir.')
        self.componentDict[self.labelList[4]]['objects'][1].delete(0, END)
        x = filedialog.askdirectory(
            initialdir=Path('.\\').parent
            )
        self.update_message(f'Got dir: {x}')
        self.componentDict[self.labelList[4]]['objects'][1].insert(0, x)

    def get_new_guuid(self):
        '''
        Generates a new GUUID for the server, this is required to create a server.
        '''
        self.update_message(f'Generating new GUUID.')
        self.componentDict['GUUID']['objects'][1].delete(0, END)
        self.componentDict['GUUID']['objects'][1].insert(0, uuid.uuid4())

    def update_server_command(self, thread_factory, thread):
        '''
        Installs / updates the alderonGamesCMD_x64
        Working.
        Tranfer this to its own thread.
        '''
        INSTALL_DIR = self.get_value(self.componentDict['InstallDir']['objects'][1])
        BRANCH = self.get_value(self.componentDict['Branch']['objects'][1])
        AG_AUTH_TOKEN = self.get_value(self.componentDict['AuthToken']['objects'][1])
        try:
            if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '':
                self.update_message(f'Updating server files.')
                if os.path.exists('AlderonGamesCMD_x64.exe'):
                    exe = os.path.abspath('AlderonGamesCMD_x64.exe')
                    sUpdateServerCommand = f'{exe} --game path-of-titans --server true --beta-branch {BRANCH} --auth-token {AG_AUTH_TOKEN} --install-dir "{INSTALL_DIR}"'
                    # This does not close out all the way, when its done the software says 'finished'
                    # if the user closes the cmd window it apears to close the server manager as well.
                    result = subprocess.run(sUpdateServerCommand, capture_output=True, text=True)
                    if result.returncode == 0:
                        #Need to check the status of the thread when we move this to the thread factory.
                        self.update_message(f'{result.stdout}')
                        self.update_message(f'Install / Update complete.')
                        thread_factory.kill_thread(thread_factory.threads[id(thread)])
                else:
                    self.update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
            else:
                self.update_message(f'Error: Auth Token, GUUID, and Install Dir must not be empty.')
        except PermissionError as e:
            self.update_message(f'{e}')

    def server_start(self):
        '''
        Works, need to add map as well.
        needs its own thread. locks up main program.
        '''
        INSTALL_DIR = self.get_value(self.componentDict['InstallDir']['objects'][1])
        SERVER_PORT = self.get_value(self.componentDict['Port']['objects'][1])
        BRANCH = self.get_value(self.componentDict['Branch']['objects'][1])
        AG_AUTH_TOKEN = self.get_value(self.componentDict['AuthToken']['objects'][1])
        SERVER_GUUID = self.get_value(self.componentDict['GUUID']['objects'][1])
        SERVER_DATABASE = self.get_value(self.componentDict['Database']['objects'][1])
        SERVER_MAP = self.get_value(self.componentDict['Map']['objects'][1])

        try:
            if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '' and not SERVER_PORT == '' and not SERVER_GUUID == '' and not SERVER_DATABASE == '' and not SERVER_MAP == '':
                self.update_message(f'Starting server .')
                if os.path.exists('AlderonGamesCMD_x64.exe'):
                    self.update_message(f'Checking path: {INSTALL_DIR}{serverExeLocation}')
                    if os.path.exists(f'{INSTALL_DIR}{serverExeLocation}'):
                        exe = f'{INSTALL_DIR}{serverExeLocation}'
                        sUpdateServerCommand = f'{INSTALL_DIR}{serverExeLocation} --game path-of-titans -ServerMap={SERVER_MAP} -Port={SERVER_PORT} -BranchKey={BRANCH} -log -AuthToken={AG_AUTH_TOKEN} -ServerGUID={SERVER_GUUID} -Database={SERVER_DATABASE}'
                        # This does not close out all the way, when its done the software says 'finished'
                        # if the user closes the cmd window it apears to close the server manager as well.
                        if subprocess.run(sUpdateServerCommand) == 0:
                            self.update_message(f'Server Started.')
                    else:
                        self.update_message(f'Make sure your install directory is setup properly or that you have\n installed the server.')
                else:
                    self.update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
            else:
                self.update_message(f'Error, one or more required options are empty')
        except PermissionError as e:
            self.update_message(f'{e}')

    def combo_box_database_selection_changed(self, event):
        selection = self.comboBox_database.get()
        print(f'Selected option: {selection}')

    def combo_box_branch_selection_changed(self, event):
        selection = self.comboBox_branch.get()
        print(f'Selected option: {selection}')

    def combo_box_map_selection_changed(self, event):
        selection = self.comboBox_map.get()
        print(f'Selected option: {selection}')

    def create_gui(self, root, tt):

        #setting title
        root.title("Path of Titans Server Manager")
        #setting window size
        width=600
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        '''
        Used to display messages to the user.
        TODO: change this to tkinter text, message does not support scrolling.
        DONE.
        '''
        self.message = Text(root, width=540, relief=RAISED, fg="#ffffff", bg="#000000")
        self.message.place(x=(600-540)/2,y=350,width=540,height=128)
        self.tkSb = Scrollbar(self.message, orient='vertical')
        self.tkSb.pack(side=RIGHT, fill='y')
        self.tkSb.config(command=self.message.yview)

        #deploy labels, more compact than having a bunch of label blocks.
        count = 0
        for l in self.labelList:
            l=tk.Label(root)
            ft = tkFont.Font(family='Times',size=10)
            l["font"] = ft
            l["fg"] = self.labelForgroundColor
            l["justify"] = self.labelJustify
            l["text"] = self.labelText[count]
            l.place(x=20,y=self.yStart,width=70,height=25)
            
            self.componentDict[self.labelList[count]] = {}
            self.componentDict[self.labelList[count]]['objects'] = {}
            self.componentDict[self.labelList[count]]['objects'] = []
            self.componentDict[self.labelList[count]]['objects'].append(l)

            self.yStart = self.yStart + self.yStep
            count = count + 1

        #deploy entry fields, more compact than having a bunch of entry blocks.
        step = 20
        count = 0
        for l in self.entryList:
            e=tk.Entry(root)
            ft = tkFont.Font(family='Times',size=10)
            e["font"] = ft
            e["fg"] = self.entryForgroundColor
            e["justify"] = self.entryJustify
            e["text"] = ''
            if l == 'InstallDir':
                e.place(x=self.entryXStart,y=step,width=256,height=self.entryHeight)
            elif l == 'GUUID':
                e.place(x=self.entryXStart,y=step,width=256,height=self.entryHeight)
            else:
                e.place(x=self.entryXStart,y=step,width=self.entryWidth,height=self.entryHeight)
            
            self.componentDict[self.labelList[count]]['objects'].append(e)

            step = step + self.yStep
            count = count + 1

        #Get the install directory for the server.
        button_get_install_Dir=tk.Button(root)
        button_get_install_Dir["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_get_install_Dir["font"] = ft
        button_get_install_Dir["fg"] = "#000000"
        button_get_install_Dir["justify"] = "center"
        button_get_install_Dir["text"] = "."
        button_get_install_Dir.place(x=self.entryXStart+258,y=140,width=16,height=self.entryHeight)
        button_get_install_Dir["command"] = lambda: self.get_install_dir()
        tt.bind_widget(button_get_install_Dir, balloonmsg='Select the directory to install the server. default is the server manager root dir.')

        #Get the install directory for the server.
        button_get_new_guuid=tk.Button(root)
        button_get_new_guuid["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_get_new_guuid["font"] = ft
        button_get_new_guuid["fg"] = "#000000"
        button_get_new_guuid["justify"] = "center"
        button_get_new_guuid["text"] = "."
        button_get_new_guuid.place(x=self.entryXStart+258,y=110,width=16,height=self.entryHeight)
        button_get_new_guuid["command"] = lambda : self.get_new_guuid()
        tt.bind_widget(button_get_new_guuid, balloonmsg='This will generate a new guuid for your server')
                                      

        #ComboBox for Database selection.
        self.comboBox_database=ttk.Combobox(
            state='readonly',
            values=['Local', 'Remote']
        )
        self.comboBox_database.set('Local')
        self.comboBox_database.bind('<<ComboboxSelected>>', self.combo_box_database_selection_changed)
        tt.bind_widget(self.comboBox_database, balloonmsg='Server can use a Local or Remote Database. Specified using -Database=Local or -Database=Remote. We recommend using a Local Database unless you plan on connecting shared character data between servers.')
        self.comboBox_database.place(x=self.entryXStart,y=170,width=self.entryWidth,height=self.entryHeight)

        #ComboBox for Branch selection.
        self.comboBox_branch=ttk.Combobox(
            state='readonly',
            values=['Production', 'demo-public-test']
        )
        self.comboBox_branch.set('Production')
        self.comboBox_branch.bind('<<ComboboxSelected>>', self.combo_box_branch_selection_changed)
        tt.bind_widget(self.comboBox_branch, balloonmsg='Right now we recommend using production as the Beta Branch, in some rare cases, you might want to use the other branch demo-public-test')
        self.comboBox_branch.place(x=self.entryXStart,y=200,width=self.entryWidth,height=self.entryHeight)

        #ComboBox for Map selection.
        self.comboBox_map=ttk.Combobox(
            state='readonly',
            values=['Island (Gondwa)', 'Panjura', 'Cerulean Island']
        )
        self.comboBox_map.set('Gondwa')
        self.comboBox_map.bind('<<ComboboxSelected>>', self.combo_box_map_selection_changed)
        self.comboBox_map.place(x=self.entryXStart,y=230,width=self.entryWidth,height=self.entryHeight)

        self.componentDict['Database']['objects'].append(self.comboBox_database)
        self.componentDict['Branch']['objects'].append(self.comboBox_branch)
        self.componentDict['Map']['objects'].append(self.comboBox_map)


        button_install_alderon_cmd=tk.Button(root)
        button_install_alderon_cmd["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_alderon_cmd["font"] = ft
        button_install_alderon_cmd["fg"] = "#000000"
        button_install_alderon_cmd["justify"] = "center"
        button_install_alderon_cmd["text"] = "Install AlderonCMD"
        button_install_alderon_cmd.place(x=30,y=256,width=120,height=25)
        downloadThread = threading.Thread(target=download_AlderonGamesCMD_thread, args=('downloadThread', self.update_message, self.threads))
        #Super cluedgy.... will fix later.
        self.threads['downloadThread'] = []
        self.threads['downloadThread'].append(downloadThread)
        self.threads['downloadThread'].append(False)
        button_install_alderon_cmd["command"] = lambda : download_thread_helper("downloadThread", self.threads)
        #button_install_alderon_cmd["command"] = lambda : download_AlderonGamesCMD(update_message, messageVar)

        button_install_server=tk.Button(root)
        button_install_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_server["font"] = ft
        button_install_server["fg"] = "#000000"
        button_install_server["justify"] = "center"
        button_install_server["text"] = "Install Server"
        button_install_server.place(x=30,y=286,width=100,height=25)
        install_thread = self.thread_factory.create(self.update_server_command, args=(self.thread_factory, 'install thread'))
        button_install_server["command"] = lambda : install_thread.start()

        button_update_server=tk.Button(root)
        button_update_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_update_server["font"] = ft
        button_update_server["fg"] = "#000000"
        button_update_server["justify"] = "center"
        button_update_server["text"] = "Update Server"
        button_update_server.place(x=30,y=316,width=100,height=25)
        button_update_server["command"] = lambda : self.update_server_command()

        button_server_run=tk.Button(root)
        button_server_run["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_server_run["font"] = ft
        button_server_run["fg"] = "#000000"
        button_server_run["justify"] = "center"
        button_server_run["text"] = "Start Server"
        button_server_run.place(x=140,y=316,width=100,height=25)
        button_server_run["command"] = lambda : self.server_start()

        button_exit_program=tk.Button(root)
        button_exit_program["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_exit_program["font"] = ft
        button_exit_program["fg"] = "#000000"
        button_exit_program["justify"] = "center"
        button_exit_program["text"] = "Exit"
        button_exit_program.place(x=250,y=316,width=100,height=25)
        button_exit_program["command"] = lambda : sys.exit(0)

        '''
        GCheckBox_779=tk.Checkbutton(root)
        ft = tkFont.Font(family='Times',size=10)
        GCheckBox_779["font"] = ft
        GCheckBox_779["fg"] = "#333333"
        GCheckBox_779["justify"] = "center"
        GCheckBox_779["text"] = "CheckBox"
        GCheckBox_779.place(x=10,y=140,width=70,height=25)
        GCheckBox_779["offvalue"] = "0"
        GCheckBox_779["onvalue"] = "1"
        GCheckBox_779["command"] = self.GCheckBox_779_command
        '''

def get_config():
    """
    Reads the config file for the server.

    Parameters:
        -None

    Returns:
    - The config data for the server.
    """
    try:
        config_dict = {}
        config.read('./config.cfg')
        for section in config.sections():
            config_dict[section] = {}
            for option in config.options(section):
                config_dict[section][option] = config.get(section, option)
        return config_dict
    except Exception as e:
        print(f'{e}')

''' now that I think of it config parser would probably be easier to manage all the config stuff. '''
def get_token_from_file():
    if not os.path.exists('./.token'):
        #create .Token file to store our auth Token
        with open('./.token', 'w+') as tFile:
            #grab token from token input field
            #once we have the token save it to the .token file
            pass

def download_thread_helper(name, threads):
    '''
    gross way of dealing with the download thread. 
    I don't like this, short on time and need to fix later.
    '''
    if name in threads:
        if not threads[name][1] == True:
            threads[name][0].start()
        else:
            threads[name][0].join()
            print(f'[Thread] - {name} killed.')
            del threads[name]

def download_AlderonGamesCMD_thread(name, update_message_func, threads):
    print(f'Threads contents: {threads}')
    if not os.path.exists('AlderonGamesCMD_x64.exe'):
        update_message_func(f'Downloading AslersonGamesCMD_x64.exe\n')
        with requests.get(AlderonGamesCMDURL, stream=True) as response:
            response.headers
            with open("AlderonGamesCMD_x64.exe", mode='wb') as file:
                count = 0
                for chunk in response.iter_content(chunk_size=10 * 1024):
                    file.write(chunk)
                    count += 1
                    if count == 10:
                        update_message_func(".", nl=False)
                        count = 0
            update_message_func('Download complete.')
            threads[name][1] = True
            print(f'Threads contents: {threads}')
    else:
        update_message_func(f'AlderonGamesCMD is already installed.')
        threads[name][1] = True
        print(f'Threads contents: {threads}')