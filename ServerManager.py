'''
Author:     OCybress
Date:       01-02-2024
Summary:    A server manager for the video game Path of Titans.
TODO:       Move update_server_command to a thread.
            Save all config information for future retrieval so the program does not forget
                its already installed the server etc.
            create run server button and function.
            Added admin UAC request.
            Changed message area to tkinter text with scroll bar.
            redirected all messages to text area.
            Fixed issue with combo box's being appended with data from BRANCH.
            Made download_AlderonGamesCMD_thread its own thread.
                Need to fix the way its killed ( its bad. )
01/05/2024  Added server_start.

Issues:     
            
'''
import os
import sys
import ctypes
from pathlib import Path
from urllib.request import urlretrieve
import requests
from datetime import datetime
import subprocess
from tkinter import ttk
import tkinter as tk
import tkinter.font as tkFont
from tkinter.tix import *
from tkinter import filedialog
import uuid
import configparser as cp
import threading

'TODO: Setup versioning..'

appGUUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'
AlderonGamesCMDURL = 'https://launcher-cdn.alderongames.com/AlderonGamesCmd-Win64.exe'
GuuidRequestUrl = 'https://duckduckgo.com/?q=random+guid&atb=v296-1&ia=answer'
tokenFromFile = True
serverExeLocation = '/PathOfTitans/Binaries/Win64/PathOfTitansServer-Win64-Shipping.exe'

config = cp.ConfigParser()
threads = {}

def is_admin():
    '''
    Request admin acess needed for running the AlderonGamesCMD_x64.exe
    '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class App:
    def __init__(self, root):
        '''
        lists of names and display text for buttons, labels, etc.
        '''
        labelList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir', 'Database', 'Branch', 'Map']
        labelText = ['Server Name', 'Auth Token', 'Port', 'GUUID', 'Install Dir', 'Database', 'Branch', 'Map']
        entryList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir']
        buttonList = ['StartServer','StopServer','UpdateServer']
        buttonText = ['Start Server','Stop Server','Update Server']

        yStart = 20
        yStep = 30
        xStart = 20
        entryXStart = 120
        labelWidth = 70
        labelHeight = 25
        labelJustify = 'left'
        labelForgroundColor = "#333333"
        entryWidth = 128
        entryHeight = 25
        entryJustify = 'left'
        entryForgroundColor = "#333333"

        '''
        {LabelName:{objects: [tkinterLabel, [tkinkerEntry|button|message]}}
        '''
        componentDict = {}

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
        messageVar = StringVar()
        message = Text(root, width=540, relief=RAISED, fg="#ffffff", bg="#000000")
        message.place(x=(600-540)/2,y=350,width=540,height=128)
        tkSb = Scrollbar(message, orient='vertical')
        tkSb.pack(side=RIGHT, fill='y')
        tkSb.config(command=message.yview)

        def get_value(entry):
            '''
            get a value stored in a tk object
            '''
            return entry.get()

        def update_message(var):
            '''
            Updates the message box in the bottom of the program.
            '''
            messageTime = str(datetime.now())[0:19]
            message.insert(END, f'\n{[messageTime]} - {var}')

        def get_install_dir():
            '''
            When the user clicks the directory icon this function
            asks them where they would like to install.
            '''
            update_message(f'Getting install dir.')
            componentDict[labelList[4]]['objects'][1].delete(0, END)
            x = filedialog.askdirectory(
                initialdir=Path('.\\').parent
                )
            update_message(f'Got dir: {x}')
            componentDict[labelList[4]]['objects'][1].insert(0, x)

        def get_new_guuid():
            '''
            Generates a new GUUID for the server, this is required to create a server.
            '''
            update_message(f'Generating new GUUID.')
            componentDict['GUUID']['objects'][1].delete(0, END)
            componentDict['GUUID']['objects'][1].insert(0, uuid.uuid4())

        def update_server_command():
            '''
            Installs / updates the alderonGamesCMD_x64
            Working.
            Tranfer this to its own thread.
            '''
            INSTALL_DIR = get_value(componentDict['InstallDir']['objects'][1])
            BRANCH = get_value(componentDict['Branch']['objects'][1])
            AG_AUTH_TOKEN = get_value(componentDict['AuthToken']['objects'][1])
            try:
                if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '':
                    update_message(f'Updating server files.')
                    if os.path.exists('AlderonGamesCMD_x64.exe'):
                        exe = os.path.abspath('AlderonGamesCMD_x64.exe')
                        sUpdateServerCommand = f'{exe} --game path-of-titans --server true --beta-branch {BRANCH} --auth-token {AG_AUTH_TOKEN} --install-dir "{INSTALL_DIR}"'
                        # This does not close out all the way, when its done the software says 'finished'
                        # if the user closes the cmd window it apears to close the server manager as well.
                        if subprocess.run(sUpdateServerCommand) == 0:
                            update_message(f'Install / Update complete.')
                    else:
                        update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
                else:
                    update_message(f'Error, one or more required options are empty')
            except PermissionError as e:
                update_message(f'{e}')

        def server_start():
            '''
            Works, need to add map as well.
            needs its own thread. locks up main program.
            '''
            INSTALL_DIR = get_value(componentDict['InstallDir']['objects'][1])
            SERVER_PORT = get_value(componentDict['Port']['objects'][1])
            BRANCH = get_value(componentDict['Branch']['objects'][1])
            AG_AUTH_TOKEN = get_value(componentDict['AuthToken']['objects'][1])
            SERVER_GUUID = get_value(componentDict['GUUID']['objects'][1])
            SERVER_DATABASE = get_value(componentDict['Database']['objects'][1])

            try:
                if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '' and not SERVER_PORT == '' and not SERVER_GUUID == '' and not SERVER_DATABASE == '':
                    update_message(f'Starting server .')
                    if os.path.exists('AlderonGamesCMD_x64.exe'):
                        update_message(f'Checking path: {INSTALL_DIR}{serverExeLocation}')
                        if os.path.exists(f'{INSTALL_DIR}{serverExeLocation}'):
                            exe = f'{INSTALL_DIR}{serverExeLocation}'
                            sUpdateServerCommand = f'{INSTALL_DIR}{serverExeLocation} --game path-of-titans -Port={SERVER_PORT} -BranchKey={BRANCH} -log -AuthToken={AG_AUTH_TOKEN} -ServerGUID={SERVER_GUUID} -Database={SERVER_DATABASE}'
                            # This does not close out all the way, when its done the software says 'finished'
                            # if the user closes the cmd window it apears to close the server manager as well.
                            if subprocess.run(sUpdateServerCommand) == 0:
                                update_message(f'Server Started.')
                        else:
                            update_message(f'Make sure your install directory is setup properly or that you have\n installed the server.')
                    else:
                        update_message(f'You need to download the AlderonGameCMD_x64.exe file first.')
                else:
                    update_message(f'Error, one or more required options are empty')
            except PermissionError as e:
                update_message(f'{e}')

        def combo_box_database_selection_changed(event):
            selection = comboBox_database.get()
            print(f'Selected option: {selection}')

        def combo_box_branch_selection_changed(event):
            selection = comboBox_branch.get()
            print(f'Selected option: {selection}')

        def combo_box_map_selection_changed(event):
            selection = comboBox_map.get()
            print(f'Selected option: {selection}')

        #deploy labels, more compact than having a bunch of label blocks.
        count = 0
        for l in labelList:
            l=tk.Label(root)
            ft = tkFont.Font(family='Times',size=10)
            l["font"] = ft
            l["fg"] = labelForgroundColor
            l["justify"] = labelJustify
            l["text"] = labelText[count]
            l.place(x=20,y=yStart,width=70,height=25)
            
            componentDict[labelList[count]] = {}
            componentDict[labelList[count]]['objects'] = {}
            componentDict[labelList[count]]['objects'] = []
            componentDict[labelList[count]]['objects'].append(l)

            yStart = yStart + yStep
            count = count + 1

        #deploy entry fields, more compact than having a bunch of entry blocks.
        step = 20
        count = 0
        for l in entryList:
            e=tk.Entry(root)
            ft = tkFont.Font(family='Times',size=10)
            e["font"] = ft
            e["fg"] = entryForgroundColor
            e["justify"] = entryJustify
            e["text"] = ''
            if l == 'InstallDir':
                e.place(x=entryXStart,y=step,width=256,height=entryHeight)
            elif l == 'GUUID':
                e.place(x=entryXStart,y=step,width=256,height=entryHeight)
            else:
                e.place(x=entryXStart,y=step,width=entryWidth,height=entryHeight)
            
            componentDict[labelList[count]]['objects'].append(e)

            step = step + yStep
            count = count + 1

        #Get the install directory for the server.
        button_get_install_Dir=tk.Button(root)
        button_get_install_Dir["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_get_install_Dir["font"] = ft
        button_get_install_Dir["fg"] = "#000000"
        button_get_install_Dir["justify"] = "center"
        button_get_install_Dir["text"] = "."
        button_get_install_Dir.place(x=entryXStart+258,y=140,width=16,height=entryHeight)
        button_get_install_Dir["command"] = lambda: get_install_dir()
        tt.bind_widget(button_get_install_Dir, balloonmsg='Select the directory to install the server. default is the server manager root dir.')

        #Get the install directory for the server.
        button_get_new_guuid=tk.Button(root)
        button_get_new_guuid["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_get_new_guuid["font"] = ft
        button_get_new_guuid["fg"] = "#000000"
        button_get_new_guuid["justify"] = "center"
        button_get_new_guuid["text"] = "."
        button_get_new_guuid.place(x=entryXStart+258,y=110,width=16,height=entryHeight)
        button_get_new_guuid["command"] = lambda : get_new_guuid()
        tt.bind_widget(button_get_new_guuid, balloonmsg='This will generate a new guuid for your server')
                                      

        #ComboBox for Database selection.
        comboBox_database=ttk.Combobox(
            state='readonly',
            values=['Local', 'Remote']
        )
        comboBox_database.set('Local')
        comboBox_database.bind('<<ComboboxSelected>>', combo_box_database_selection_changed)
        tt.bind_widget(comboBox_database, balloonmsg='Server can use a Local or Remote Database. Specified using -Database=Local or -Database=Remote. We recommend using a Local Database unless you plan on connecting shared character data between servers.')
        comboBox_database.place(x=entryXStart,y=170,width=entryWidth,height=entryHeight)

        #ComboBox for Branch selection.
        comboBox_branch=ttk.Combobox(
            state='readonly',
            values=['Production', 'demo-public-test']
        )
        comboBox_branch.set('Production')
        comboBox_branch.bind('<<ComboboxSelected>>', combo_box_branch_selection_changed)
        tt.bind_widget(comboBox_branch, balloonmsg='Right now we recommend using production as the Beta Branch, in some rare cases, you might want to use the other branch demo-public-test')
        comboBox_branch.place(x=entryXStart,y=200,width=entryWidth,height=entryHeight)

        #ComboBox for Map selection.
        comboBox_map=ttk.Combobox(
            state='readonly',
            values=['Gondwa', 'Panjura']
        )
        comboBox_map.set('Gondwa')
        comboBox_map.bind('<<ComboboxSelected>>', combo_box_map_selection_changed)
        comboBox_map.place(x=entryXStart,y=230,width=entryWidth,height=entryHeight)

        componentDict['Database']['objects'].append(comboBox_database)
        componentDict['Branch']['objects'].append(comboBox_branch)
        componentDict['Map']['objects'].append(comboBox_map)


        button_install_alderon_cmd=tk.Button(root)
        button_install_alderon_cmd["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_alderon_cmd["font"] = ft
        button_install_alderon_cmd["fg"] = "#000000"
        button_install_alderon_cmd["justify"] = "center"
        button_install_alderon_cmd["text"] = "Install AlderonCMD"
        button_install_alderon_cmd.place(x=30,y=256,width=120,height=25)
        downloadThread = threading.Thread(target=download_AlderonGamesCMD_thread, args=('downloadThread', update_message, messageVar))
        #Super cluedgy.... will fix later.
        threads['downloadThread'] = []
        threads['downloadThread'].append(downloadThread)
        threads['downloadThread'].append(False)
        button_install_alderon_cmd["command"] = lambda : download_thread_helper("downloadThread")
        #button_install_alderon_cmd["command"] = lambda : download_AlderonGamesCMD(update_message, messageVar)

        button_install_server=tk.Button(root)
        button_install_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_server["font"] = ft
        button_install_server["fg"] = "#000000"
        button_install_server["justify"] = "center"
        button_install_server["text"] = "Install Server"
        button_install_server.place(x=30,y=286,width=100,height=25)
        button_install_server["command"] = lambda : update_server_command()

        button_update_server=tk.Button(root)
        button_update_server["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_update_server["font"] = ft
        button_update_server["fg"] = "#000000"
        button_update_server["justify"] = "center"
        button_update_server["text"] = "Update Server"
        button_update_server.place(x=30,y=316,width=100,height=25)
        button_update_server["command"] = lambda : update_server_command()

        button_server_run=tk.Button(root)
        button_server_run["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_server_run["font"] = ft
        button_server_run["fg"] = "#000000"
        button_server_run["justify"] = "center"
        button_server_run["text"] = "Start Server"
        button_server_run.place(x=140,y=316,width=100,height=25)
        button_server_run["command"] = lambda : server_start()

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

def download_thread_helper(name):
    '''
    gross way of dealing with the download thread. 
    I don't like this, short on time and need to fix later.
    '''
    if not threads[name][1] == True:
        threads[name][0].start()
    else:
        threads[name][0].join()
        print(f'[Thread] - {name} killed.')
        del threads[name]

def download_AlderonGamesCMD_thread(name, update_message_func, messageVar):
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
                        messageVar.set(messageVar.get() + ".")
                        count = 0
            update_message_func('Download complete.')
            threads[name][1] = True
            print(f'Threads contents: {threads}')
    else:
        update_message_func(f'AlderonGamesCMD is already installed.')
        threads[name][1] = True
        print(f'Threads contents: {threads}')

if __name__ == "__main__":
    root = tkinter.tix.Tk()
    tt = Balloon(root)
    app = App(root)
    if is_admin():
        root.mainloop()
    else:
        '''
        Pulled from Stackoverflow: https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
        Martín De la Fuente
        Notes:
        Also note that if you converted you python script into an executable file (using tools like py2exe, cx_freeze, pyinstaller) then you should use sys.argv[1:] instead of sys.argv in the fourth parameter.

        Some of the advantages here are:

        No external libraries required. It only uses ctypes and sys from standard library.
        Works on both Python 2 and Python 3.
        There is no need to modify the file resources nor creating a manifest file.
        If you don't add code below if/else statement, the code won't ever be executed twice.
        You can get the return value of the API call in the last line and take an action if it fails (code <= 32). Check possible return values here.
        You can change the display method of the spawned process modifying the sixth parameter.
        '''
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
