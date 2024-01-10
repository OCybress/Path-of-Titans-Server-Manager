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
import atexit
import signal
from functools import partial
import tkinter as tk
from tkinter import ttk
from tkinter.tix import Balloon
from tkinter.tix import *
from appModule import App
import log
from err import error
from threadFactory import ThreadFactory

'TODO: Setup versioning..'
appGUUID = 'e8f0cabc-14e4-4d04-952b-613e6112400f'

# Set the version and module information
__version__ = '0.10'
mod_name, branch = __name__, str(__file__.split(os.path.sep)[-2])
VERSION_STRING = f'Loading {mod_name} module, version {__version__}, from branch {branch}.'

# Configure logging
log.setup_logging()
log.write('//////////////////////////////////////////////////////////////////////////\n//               Program Start                                          //\n//////////////////////////////////////////////////////////////////////////')
log.write('Loading modules.\n' + '\n'.join([log.VERSION_STRING, VERSION_STRING, 'Loading modules complete.']))



def is_admin():
    '''
    Check if the current user has administrative privileges.

    Returns:
        bool: True if the user has administrative privileges, False otherwise.
    '''
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def cleanup_function(thread_factory):
    """
    Cleans up and kills all threads created by the ThreadFactory.

    Args:
        thread_factory (ThreadFactory): The ThreadFactory object responsible for creating threads.

    Returns:
        None
    """
    # Kill the thread using the ThreadFactory
    log.write(f'Killing Threads.')
    for thread in thread_factory.threads:
        log.write(f'Killing thread Id {id(thread)}.')
        thread_factory.kill_thread(id(thread))
    log.write(f'All threads killed. Main thread going down.')
        
# Handle SIGTERM signal
def signal_handler(signum, frame, thread_factory):
    """
    Signal handler function that is called when a signal is received.
    
    Args:
        signum (int): The signal number.
        frame (frame): The current stack frame.
        thread_factory (ThreadFactory): An instance of the ThreadFactory class.
    """
    log.write(f"Received signal {signum}. Cleaning up...")
    cleanup_funcrion(thread_factory)
    sys.exit(0)

def main():
    """
    The main function of the server manager program.
    It initializes the GUI, starts monitoring threads, registers cleanup handlers,
    and handles the execution flow based on whether the program is run as an administrator or not.
    """
    try:
        root = tkinter.tix.Tk()
        tt = Balloon(root)

        thread_factory = ThreadFactory(log)
        # Start monitoring threads
        thread_factory.start_monitoring()

        app = App(root, tt, thread_factory, True)

        log.write("registering cleanup handler...")
        # Register the cleanup function for a normal exit.
        atexit.register(cleanup_function, thread_factory)
        cleanup_handler = partial(signal_handler, thread_factory=thread_factory)
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)

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
    except SystemExit:
        log.write('Forceful exit, running cleanup.')
        cleanup_function(thread_factory)
        sys.exit(0)


if __name__ == "__main__":
    main()