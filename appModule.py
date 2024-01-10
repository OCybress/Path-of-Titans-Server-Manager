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
                        added settingsEditor.py module for editing Game.ini settings in app.
                             SettingsEditor window is dynamicly created based on the contents of Game.ini
                             if nothing exists in game.ini the window will not populate any settings.
                             will add feature later to add settings, so user does not 
                             have to find Game.ini and edit manually.
                        added a proper menu bar. will migrate buttons to the menu bar.
            01-08-2024  integrated settings Editor.
                        integrated config manager.
                        Moved all threads to Thread Factory
                        Program now reads ./config/config.ini to load user saved settings ( profile ) 
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
from settingsEditor import GameSettingsEditor
import log
from err import error
from configManager import ConfigManager

'TODO: Setup versioning..'

appGUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'
AlderonGamesCMDURL = 'https://launcher-cdn.alderongames.com/AlderonGamesCmd-Win64.exe'
GUIDRequestUrl = 'https://duckduckgo.com/?q=random+guid&atb=v296-1&ia=answer'
tokenFromFile = True
serverExeLocation = '/PathOfTitans/Binaries/Win64/PathOfTitansServer-Win64-Shipping.exe'

#Tool tip messages.
MSG_TT_GET_INSTALL_DIR = 'Select the directory to install the server. default is the server manager root dir.'
MSG_TT_GENERATE_GUID = 'This will generate a new GUID for your server, if you already have one in config it should show up here.'
MSG_TT_SERVER_DATABASE = 'Server can use a Local or Remote Database. Specified using -Database=Local or -Database=Remote. We recommend using a Local Database unless you plan on connecting shared character data between servers.'
MSG_TT_SERVER_BRANCH = 'Right now we recommend using production as the Beta Branch, in some rare cases, you might want to use the other branch demo-public-test'
MSG_TT_SERVER_MAP = 'Select the map you want to host.'
MSG_TT_ALDERON_DOWNLOAD = 'Downloads the AlderonGamesCMD_x64.exe'
MSG_TT_SERVER_INSTALL = 'Downloads the Path of Titans server files.'
MSG_TT_SERVER_UPDATE = 'Updates the Path of Titans server files.'

class App:
    def __init__(self, root, tt, thread_factory, dev=False):
            '''
            Initialize the appModule class.

            Args:
                root (tkinter.Tk): The root window of the application.
                tt (ttk.Style): The ttk style object.
                thread_factory (ThreadFactory): The thread factory object.
                dev (bool, optional): Flag indicating if the application is in development mode. Defaults to False.
            '''
            self.development = dev

            self.labelList = ['ServerName', 'AuthToken', 'Port', 'GUID', 'InstallDir', 'Database', 'Branch', 'Map']
            self.labelText = ['Server Name', 'Auth Token', 'Port', 'GUID', 'Install Dir', 'Database', 'Branch', 'Map']
            self.entryList = ['ServerName', 'AuthToken', 'Port', 'GUID', 'InstallDir']
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

            #Server config information
            self.INSTALL_DIR = StringVar()
            self.SERVER_NAME = StringVar()
            self.SERVER_PORT = StringVar()
            self.SERVER_BRANCH = StringVar()
            self.SERVER_DATABASE = StringVar()
            self.SERVER_GUID = StringVar()
            self.AUTH_TOKEN = StringVar()

            '''
            {LabelName:{objects: [tkinterLabel, [tkinkerEntry|button|message]}}
            '''
            self.componentDict = {}

            self.configManager = ConfigManager('./config/config.ini')
            self.thread_factory = thread_factory
            self.threads = {}
            self.root = root

            # Create the menu bar
            menubar = tk.Menu(root)
            
            # Create the File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="New", command=self.new_file)
            file_menu.add_command(label="Open", command=self.open_file)
            file_menu.add_command(label="Save", command=self.save_file)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=root.destroy)
            
            # Add the File menu to the menu bar
            menubar.add_cascade(label="File", menu=file_menu)

            # Create the Edit menu
            edit_menu = tk.Menu(menubar, tearoff=0)
            edit_menu.add_command(label="Game.ini", command=self.edit_game_ini)
            
            # Add the Edit menu to the menu bar
            menubar.add_cascade(label="Edit", menu=edit_menu)
            
            # Set the menu bar
            self.root.config(menu=menubar)
            self.create_gui(self.root, tt)

    def new_file(self):
        print("New file")

    def open_file(self):
        print("Open file")

    def save_file(self):
        print("Save file")

    def edit_game_ini(self):
        """
        Opens the GameSettingsEditor window to edit the game.ini file.

        This method initializes and opens the GameSettingsEditor window, which allows the user to modify the game.ini file.
        The window is created as a Toplevel widget and is transient to the root window.
        The method waits for the settings_editor_window to be closed before continuing execution.
        """
        settings_editor_window = tk.Toplevel(self.root)
        settings_editor = GameSettingsEditor(settings_editor_window, self.update_message, self.INSTALL_DIR)
        settings_editor_window.transient(self.root)
        settings_editor_window.grab_set()
        self.root.wait_window(settings_editor_window)

    def copy(self):
        print("Copy")

    def paste(self):
        print("Paste")

    def get_value(self, entry):
        '''
        Get the value stored in a Tkinter entry object.

        Parameters:
            entry (Tkinter.Entry): The Tkinter entry object.

        Returns:
            str: The value stored in the entry object.
        '''
        return entry.get()

    def get_external_ip(self):
            """
            Retrieves the external IP address of the server.

            Returns:
                str: The external IP address of the server.
            
            Raises:
                Exception: If there is an error while fetching the external IP address.
            """
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
            """
            Get the internal IP address of the host machine.

            Returns:
                str: The internal IP address of the host machine.
            
            Raises:
                Exception: If an error occurs while retrieving the IP address.
            """
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

            Returns:
            - str: The selected installation directory.
            '''
            self.update_message(f'Getting install dir.')
            self.componentDict[self.labelList[4]]['objects'][1].delete(0, END)
            x = filedialog.askdirectory(
                initialdir=Path('.\\').parent
                )
            self.update_message(f'Got dir: {x}')
            self.componentDict[self.labelList[4]]['objects'][1].insert(0, x)
            self.INSTALL_DIR = x
            return x

    def get_new_guid(self):
            '''
            Returns:
                str: A new GUID generated using the uuid.uuid4() function.
            '''
            self.update_message(f'Generating new GUID.')
            self.componentDict['GUID']['objects'][1].delete(0, END)
            self.componentDict['GUID']['objects'][1].insert(0, uuid.uuid4())

    def update_server_command(self, thread_factory, thread):
        '''
        Installs / updates the alderonGamesCMD_x64
        Working.
        Tranfer this to its own thread.
        '''
        self.INSTALL_DIR = self.get_value(self.componentDict['InstallDir']['objects'][1])
        BRANCH = self.get_value(self.componentDict['Branch']['objects'][1])
        AG_AUTH_TOKEN = self.get_value(self.componentDict['AuthToken']['objects'][1])
        try:
            if not self.INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '':
                self.update_message(f'Updating server files.')
                if os.path.exists('AlderonGamesCMD_x64.exe'):
                    self.update_message('AlderonGamesCMD_x64.exe found.')
                    exe = os.path.abspath('AlderonGamesCMD_x64.exe')
                    sUpdateServerCommand = f'{exe} --game path-of-titans --server true --beta-branch {BRANCH} --auth-token {AG_AUTH_TOKEN} --install-dir {self.INSTALL_DIR}'
                    self.update_message(f'running command: {sUpdateServerCommand}')
                    try:
                        result = subprocess.run(sUpdateServerCommand, capture_output=True, text=True, timeout=30)

                        if result.returncode == 0:
                            if result.stdout:
                                self.update_message(f'{result.stdout}')
                                self.update_message(f'Install / Update complete.')
                                thread_factory.kill_thread(thread_factory.threads[id(thread)])
                            if result.stderr:
                                self.update_message(f'{result.stderr}')
                                self.update_message(f'Install / Update complete.')
                                thread_factory.kill_thread(thread_factory.threads[id(thread)])

                    except subprocess.TimeoutExpired:
                        self.update_message('The command took too long to complete')
                else:
                    self.update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
                    thread_factory.kill_thread(thread_factory.threads[id(thread)])
            else:
                self.update_message(f'Error: Auth Token, GUID, and Install Dir must not be empty.')
                thread_factory.kill_thread(thread_factory.threads[id(thread)])
        except PermissionError as e:
            self.update_message(f'{e}')
            thread_factory.kill_thread(thread_factory.threads[id(thread)])

    def server_start(self, thread_factory, thread):
        """
        Starts the server with the given parameters.

        This function retrieves the necessary parameters from the application's GUI fields, constructs the server start command, and then runs it using the subprocess module. If the server starts successfully, it updates the GUI with a success message. If there's an error (like a missing executable or a permission error), it updates the GUI with an error message and kills the thread.

        Parameters:
        thread_factory (ThreadFactory): An instance of the ThreadFactory class used to manage threads.
        thread (Thread): The thread that this function is running on.

        Returns:
        None
        """

        INSTALL_DIR = self.get_value(self.componentDict['InstallDir']['objects'][1])
        SERVER_PORT = self.get_value(self.componentDict['Port']['objects'][1])
        BRANCH = self.get_value(self.componentDict['Branch']['objects'][1])
        AG_AUTH_TOKEN = self.get_value(self.componentDict['AuthToken']['objects'][1])
        SERVER_GUID = self.get_value(self.componentDict['GUID']['objects'][1])
        SERVER_DATABASE = self.get_value(self.componentDict['Database']['objects'][1])
        SERVER_MAP = self.get_value(self.componentDict['Map']['objects'][1])
        print(f'{INSTALL_DIR}:{SERVER_PORT}:{BRANCH}:{AG_AUTH_TOKEN}:{SERVER_GUID}:{SERVER_DATABASE}:{SERVER_MAP}')

        try:
            if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '' and not SERVER_PORT == '' and not SERVER_GUID == '' and not SERVER_DATABASE == '':
                self.update_message(f'Starting server .')
                if os.path.exists('AlderonGamesCMD_x64.exe'):
                    self.update_message(f'Checking path: {INSTALL_DIR}{serverExeLocation}')
                    if os.path.exists(f'{INSTALL_DIR}{serverExeLocation}'):
                        exe = f'{INSTALL_DIR}{serverExeLocation}'
                        sServerStartCommand = f'{INSTALL_DIR}{serverExeLocation} --game path-of-titans -Port={SERVER_PORT} -BranchKey={BRANCH} -log -AuthToken={AG_AUTH_TOKEN} -ServerGUID={SERVER_GUID} -Database={SERVER_DATABASE}'
                        result = subprocess.run(sServerStartCommand, capture_output=True, text=True)

                        if result.returncode == 0:
                            if result.stdout:
                                self.update_message(f'{result.stdout}')
                                self.update_message(f'Server is running.')
                    else:
                        self.update_message(f'Make sure your install directory is setup properly or that you have\n installed the server.')
                        thread_factory.kill_thread(thread_factory.threads[id(thread)])
                else:
                    self.update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
                    thread_factory.kill_thread(thread_factory.threads[id(thread)])
            else:
                self.update_message(f'Error, one or more required options are empty')
                thread_factory.kill_thread(thread_factory.threads[id(thread)])
        except PermissionError as e:
            self.update_message(f'{e}')
            thread_factory.kill_thread(thread_factory.threads[id(thread)])

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
        """
        Creates the graphical user interface for the Path of Titans Server Manager.

        Parameters:
        - root: The root Tkinter window object.
        - tt: The ToolTip object for displaying tooltips.

        Returns:
        None
        """
        # Code for creating the GUI...
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

        if self.development:
            self.update_message('Warning, development mode is enabled.')

        #Config file read.
        self.update_message('Reading configuration information.')
        self.config = self.configManager.read_entire_config()
        self.INSTALL_DIR = self.config['PATHS']['installdir']
        self.update_message('Config file read. Loading values.')

        # Deploy labels, more compact than having a bunch of label blocks.
        for count, label in enumerate(self.labelList):
            l = tk.Label(
                root, 
                font=tkFont.Font(family='Times', size=10), 
                fg=self.labelForgroundColor, 
                justify=self.labelJustify, 
                text=self.labelText[count]
            )
            l.place(x=20, y=self.yStart, width=70, height=25)
            
            self.componentDict[label] = {'objects': [l]}

            self.yStart += self.yStep

        # Deploy entry fields, more compact than having a bunch of entry blocks.
        step = 20
        has_run_for_guid = False
        if self.development:
            self.update_message('Getting token from .token')
            self.AG_AUTH_TOKEN = get_token_from_file(self.update_message)
        for count, l in enumerate(self.entryList):
            e = tk.Entry(root, font=tkFont.Font(family='Times', size=10), fg=self.entryForgroundColor, justify=self.entryJustify)
            
            for section in self.config:
                option = self.config[section].get(l.lower())
                if l == 'AuthToken':
                    e.insert(0, self.AG_AUTH_TOKEN)
                elif option:
                    e.insert(0, option)

            width = 256 if l in ['InstallDir', 'AuthToken','GUID'] else self.entryWidth
            e.place(x=self.entryXStart, y=step, width=width, height=self.entryHeight)
            
            self.componentDict[self.labelList[count]]['objects'].append(e)

            step += self.yStep

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
        button_get_new_guid=tk.Button(root)
        button_get_new_guid["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_get_new_guid["font"] = ft
        button_get_new_guid["fg"] = "#000000"
        button_get_new_guid["justify"] = "center"
        button_get_new_guid["text"] = "."
        button_get_new_guid.place(x=self.entryXStart+258,y=110,width=16,height=self.entryHeight)
        button_get_new_guid["command"] = lambda : self.get_new_guid()
        tt.bind_widget(button_get_new_guid, balloonmsg='This will generate a new guid for your server')
                                      
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
        tt.bind_widget(self.comboBox_map, balloonmsg=MSG_TT_SERVER_MAP)

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
        self.install_alderon_thread = self.thread_factory.create(download_AlderonGamesCMD, args=(self.thread_factory, 'install alderon thread', self.update_message))
        button_install_alderon_cmd["command"] = lambda : self.install_alderon_thread.start()
        tt.bind_widget(button_install_alderon_cmd, balloonmsg='Downloads the AlderonGamesCMD_x64.exe')

        button_install_server=tk.Button(root)
        button_install_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_server["font"] = ft
        button_install_server["fg"] = "#000000"
        button_install_server["justify"] = "center"
        button_install_server["text"] = "Install Server"
        button_install_server.place(x=30,y=286,width=100,height=25)
        #if 'install thread' in self.thread_factory.threads:
        #    self.thread_factory.kill_thread(id(self.thread_factory.threads['install thread']))
        self.install_thread = self.thread_factory.create(self.update_server_command, args=(self.thread_factory, 'install thread'))
        button_install_server["command"] = lambda : self.install_thread.start()
        tt.bind_widget(button_install_server, balloonmsg='Downloads the Path of Titans server files.')

        button_update_server=tk.Button(root)
        button_update_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_update_server["font"] = ft
        button_update_server["fg"] = "#000000"
        button_update_server["justify"] = "center"
        button_update_server["text"] = "Update Server"
        button_update_server.place(x=30,y=316,width=100,height=25)
        self.update_thread = self.thread_factory.create(self.update_server_command, args=(self.thread_factory, 'update thread'))
        button_install_server["command"] = lambda : self.update_thread.start()
        tt.bind_widget(button_install_server, balloonmsg='Updates the Path of Titans server files.')

        button_server_run=tk.Button(root)
        button_server_run["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_server_run["font"] = ft
        button_server_run["fg"] = "#000000"
        button_server_run["justify"] = "center"
        button_server_run["text"] = "Start Server"
        button_server_run.place(x=140,y=316,width=100,height=25)
        self.run_server_thread = self.thread_factory.create(self.server_start, args=(self.thread_factory, 'run server thread'))
        button_server_run["command"] = lambda : self.run_server_thread.start()

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

''' Use this for development. pulls from .token instead of config file, don't upload your token to github. '''
def get_token_from_file(update_message_func):
    """
    Retrieves the token from the .token file.

    Args:
        update_message_func (function): A function used to update the message.

    Returns:
        str: The token read from the .token file.
    """
    if not os.path.exists('./.token'):
        update_message_func('You need to create a .token file and place your token inside. This is only used for development.')
    else:
        update_message_func('.token file exists.')
        with open('.token', 'r') as tFile:
            token = tFile.read()
            return token

def download_AlderonGamesCMD(thread_factory, thread, update_message_func):
    """
    Downloads AlderonGamesCMD_x64.exe if it doesn't already exist in the current directory.
    
    Args:
        thread_factory (ThreadFactory): An instance of the ThreadFactory class.
        thread (Thread): The current thread.
        update_message_func (function): A function to update the download progress message.
    """
    if not os.path.exists('AlderonGamesCMD_x64.exe'):
        update_message_func(f'Downloading AlderonGamesCMD_x64.exe\n')
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
            thread_id = id(thread)
            if thread_id in thread_factory.threads:
                thread_factory.kill_thread(thread_factory.threads[thread_id])
            else:
                print(f'Thread with id {thread_id} does not exist')
    else:
        update_message_func(f'AlderonGamesCMD is already installed.')
        thread_id = id(thread)
        if thread_id in thread_factory.threads:
            thread_factory.kill_thread(thread_factory.threads[thread_id])
        else:
            print(f'Thread with id {thread_id} does not exist')