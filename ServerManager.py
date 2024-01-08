'''
Author:     OCybress
Date:       01-02-2024
Summary:    A server manager for the video game Path of Titans.
Updates     Move update_server_command to a thread.
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
01/08/2024  Moved App class to its own module.
            Added log, err modules.


Issues:

TODO:       [x] Move app class to its own module.
            Make a thread factory module.
            Move all threads to thread factory.
            Add logging module.
            Add config module.
            Add ability to edit settings in game.ini
            Group buttons and entry's with frames for better ux flow.    
            
'''
import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter.tix import Balloon
from tkinter.tix import *
from app_module import App
import log
from err import error

'TODO: Setup versioning..'
appGUUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'

# Set the version and module information
__version__ = '0.10'
mod_name, branch = __name__, str(__file__.split(os.path.sep)[-2])
VERSION_STRING = f'Loading {mod_name} module, version {__version__}, from branch {branch}.'

# Configure logging
log.setup_logging(f'.\log.txt')
log.write('//////////////////////////////////////////////////////////////////////////\n//               Program Start                                          //\n//////////////////////////////////////////////////////////////////////////')
log.write('Loading modules.\n' + '\n'.join([log.VERSION_STRING, VERSION_STRING, 'Loading modules complete.']))

def is_admin():
    '''
    Request admin acess needed for running the AlderonGamesCMD_x64.exe
    '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    root = tkinter.tix.Tk()
    tt = Balloon(root)

    #thread_factory = ThreadFactory()

    app = App(root, tt) #(root, thread_factory)

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


if __name__ == "__main__":
    main()