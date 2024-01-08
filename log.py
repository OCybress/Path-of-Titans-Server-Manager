'''
AUTHOR  :   Jeremy Goss
Date    :   2-18-2020
Summary :   A pretty logger, writes anything to a log file.
VERSION History
0x01    : 
            Initial
0x02    :  
            
'''

import os
import inspect
from datetime import datetime
from pprint import pprint as print

import log
from err import error

__version__ = '01.00'

mod_name = __name__
branch = str(__file__.split(os.path.sep)[-2])
VERSION_STRING = f'Loading {mod_name} module, version {__version__}, from branch {branch}.'
print(VERSION_STRING)

o_time = str(datetime.now())[0:10]

l_file = object()
output = 1

def setup_logging(path='./logs/log') -> None:
    """
    Sets up the logging file.

    Parameters:
    - path: The path for the log file.

    Returns:
    - None
    """
    try:
        global l_file
        print(f'Setting up log.')
        if os.path.exists(f'{path}-{o_time}.log'):
            print(f'Log exists, using existing log.')
            l_file = open(f'{path}-{o_time}.log', 'a')
        else:
            print(f'Log does not exist, creating new log.')
            l_file = open(f'{path}-{o_time}.log', 'w')
    except Exception as e:
        log.write(error(e, mod_name))

def write(data, prepend_timestamp=True, debug=False):
    """
    Writes data to the log file.

    Parameters:
    - data: The data to be written.
    - prepend_timestamp: Boolean flag to indicate whether to prepend a timestamp.
    - debug: Boolean flag to indicate whether to include debug information.

    Returns:
    - None
    """
    try:
        global l_file

        frame = inspect.stack()[2]
        callers = [frame.function]

        for frame_info in inspect.stack():
            callers.append('__main__' if frame_info.function == '<module>' else frame_info.function)

        caller_str = ' --> '.join(reversed(callers))
        w_time = str(datetime.now())[10:19]
        log_message = f'Module: {__name__} | {caller_str} | Data:\n{data}'

        log_entry = f'[{w_time}] \r\n-{log_message}\r\n' if prepend_timestamp and debug else f'-{data}\r\n'
        l_file.write(log_entry)
    except Exception as e:
        error(e, mod_name)
'''
previous_caller = ''

def write(data, t=True, debug=False):
    """
    Writes data to the log file.

    Parameters:
    - data: The data to be written.
    - t: Boolean flag to indicate whether to prepend a timestamp.

    Returns:
    - None
    """
    try:
        global l_file
        global previous_caller

        frame = inspect.stack()[2]
        callers = [frame.function]

        for frame_info in iter(inspect.stack()):
            callers.append('__main__' if frame_info.function == '<module>' else frame_info.function)

        caller_str = ' --> '.join(reversed(callers))

        w_time = str(datetime.now())[10:19]
        log_message = f'Module: {__name__} | {caller_str} | Data:\n{data}'

        if t:
            if debug:
                l_file.write(f'[{w_time}] \r\n-{log_message}\r\n')
            else:
                l_file.write(f'[{w_time}] \r\n-{data}\r\n')
        else:
            if debug:
                l_file.write(f'-{data}\r\n')
            else:
                l_file.write(f'-{log_message}\r\n')
    except Exception as e:
        error(e, mod_name)
'''

def close_log():
    """
    Closes the log file.

    Returns:
    - None
    """
    try:
        global l_file
        l_file.close()
    except Exception as e:
        log.write(error(e, mod_name))
