'''
Author:     OCybress
Date:       01-02-2024
Summary:    A server manager for the video game Path of Titans.
TODO:       Everything..
'''
import os
import sys
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

appGUUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'
AlderonGamesCMDURL = 'https://launcher-cdn.alderongames.com/AlderonGamesCmd-Win64.exe'
GuuidRequestUrl = 'https://duckduckgo.com/?q=random+guid&atb=v296-1&ia=answer'
tokenFromFile = True

config = cp.ConfigParser()

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

        def get_value(entry):
            return entry.get()

        def get_install_dir():
            print(f'Getting install dir.')
            componentDict[labelList[4]]['objects'][1].delete(0, END)
            x = filedialog.askdirectory(
                initialdir=Path('.\\').parent
                )
            print(f'Got dir: {x}')
            componentDict[labelList[4]]['objects'][1].insert(0, x)

        def get_new_guuid():
            componentDict['GUUID']['objects'][1].delete(0, END)
            componentDict['GUUID']['objects'][1].insert(0, uuid.uuid4())

        def update_server_command():
            INSTALL_DIR = get_value(componentDict['InstallDir']['objects'][1])
            BRANCH = get_value(componentDict['Branch']['objects'][1])
            AG_AUTH_TOKEN = get_value(componentDict['AuthToken']['objects'][1])

            if not INSTALL_DIR == '' and not BRANCH == '' and not AG_AUTH_TOKEN == '':
                if os.path.exists('AlderonGamesCMD_x64.exe'):
                    sUpdateServerCommand = f'AlderonGamesCMD_x64.exe --game path-of-titans --server true --beta-branch {BRANCH} --auth-token {AG_AUTH_TOKEN} --install-dir {INSTALL_DIR}'
                    print(f'{sUpdateServerCommand}')
                    subprocess.run([sUpdateServerCommand])
                else:
                    print(f'You need to download the AlderonGameCMD_x64.exe file first.')
            else:
                print(f'Error, one or more required options are empty')

        def combo_box_branch_selection_changed(event):
            selection = comboBox_branch.get()
            print(f'Selected option: {selection}')

        def combo_box_map_selection_changed(event):
            selection = comboBox_map.get()
            print(f'Selected option: {selection}')
        
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
        comboBox_database.bind('<<ComboboxSelected>>', combo_box_branch_selection_changed)
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

        componentDict['Branch']['objects'].append(comboBox_database)
        componentDict['Branch']['objects'].append(comboBox_branch)
        componentDict['Branch']['objects'].append(comboBox_map)


        button_install_alderon_cmd=tk.Button(root)
        button_install_alderon_cmd["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        button_install_alderon_cmd["font"] = ft
        button_install_alderon_cmd["fg"] = "#000000"
        button_install_alderon_cmd["justify"] = "center"
        button_install_alderon_cmd["text"] = "Install AlderonCMD"
        button_install_alderon_cmd.place(x=30,y=256,width=120,height=25)
        button_install_alderon_cmd["command"] = lambda : download_AlderonGamesCMD()

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
        button_update_server["command"] = lambda : update_server_command(get_value(componentDict[labelList[4]]['objects'][1]),
                                                            get_value(componentDict[labelList[5]]['objects'][1]),
                                                            get_value(componentDict[labelList[1]]['objects'][1])
                                                            )

        '''
        Gives controll of the text of the label. For testing only.
        '''
        #componentDict[labelList[0]]['objects'][0]['text'] = 'testing'
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

        GListBox_381=tk.Listbox(root)
        GListBox_381["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        GListBox_381["font"] = ft
        GListBox_381["fg"] = "#333333"
        GListBox_381["justify"] = "center"
        GListBox_381.place(x=20,y=250,width=80,height=25)

        GMessage_159=tk.Message(root)
        ft = tkFont.Font(family='Times',size=10)
        GMessage_159["font"] = ft
        GMessage_159["fg"] = "#333333"
        GMessage_159["justify"] = "center"
        GMessage_159["text"] = "Message"
        GMessage_159.place(x=20,y=300,width=80,height=25)
        '''
    

    def GButton_909_command(self):
        print("command")


    def GCheckBox_779_command(self):
        print("command")


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

def download_AlderonGamesCMD():
    if not os.path.exists('AlderonGamesCMD_x64.exe'):
        #path, headers = urlretrieve(AlderonGamesCMDURL, 'AdleronGamesCMD_x64.exe')
        #for name, value in headers.items():
        #    print(f'{name, value}')
        with requests.get(AlderonGamesCMDURL, stream=True) as response:
            response.headers
            with open("AlderonGamesCMD_x64.exe", mode='wb') as file:
                for chunk in response.iter_content(chunk_size=10 * 1024):
                    file.write(chunk)
    else:
        print(f'AlderonGamesCMD is already installed.')



if __name__ == "__main__":
    root = tkinter.tix.Tk()
    tt = Balloon(root)
    app = App(root)
    root.mainloop()
