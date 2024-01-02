'''
Author:     OCybress
Date:       01-02-2024
Summary:    A server manager for the video game Path of Titans.
'''
import os
import sys
from datetime import datetime
import tkinter as tk
import tkinter.font as tkFont

class App:
    def __init__(self, root):
        sStartServerCommand = f''
        sStopServerCommand = f''
        sUpdateServerCommand = f''


        labelList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir', 'Branch']
        labelText = ['Server Name', 'Auth Token', 'Port', 'GUUID', 'Install Dir', 'Branch']
        entryList = ['ServerName', 'AuthToken', 'Port', 'GUUID', 'InstallDir', 'Branch']
        yStart = 20
        yStep = 30
        xStart = 20
        entryXStart = 120
        labelWidth = 70
        labelHeight = 25
        labelJustify = 'left'
        labelForgroundColor = "#333333"

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

        step = 20
        count = 0
        for l in entryList:
            e=tk.Entry(root)
            ft = tkFont.Font(family='Times',size=10)
            e["font"] = ft
            e["fg"] = labelForgroundColor
            e["justify"] = labelJustify
            e["text"] = ''
            e.place(x=entryXStart,y=step,width=70,height=25)
            
            componentDict[labelList[count]]['objects'].append(e)

            step = step + yStep
            count = count + 1

        '''
        Gives controll of the text of the label. For testing only.
        '''
        #componentDict[labelList[0]]['objects'][0]['text'] = 'testing'

        GButton_909=tk.Button(root)
        GButton_909["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        GButton_909["font"] = ft
        GButton_909["fg"] = "#000000"
        GButton_909["justify"] = "center"
        GButton_909["text"] = "Button"
        GButton_909.place(x=30,y=90,width=70,height=25)
        GButton_909["command"] = self.GButton_909_command

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

    def GButton_909_command(self):
        print("command")


    def GCheckBox_779_command(self):
        print("command")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
