import os
import sys
from datetime import datetime

def error(*args):
    """
    Logs and returns an error message with the current timestamp, module name, line number,
    error type, and error cause.

    Args:
        *args: Variable number of arguments. The first argument should be the error object,
               the second argument should be the module name.

    Returns:
        str: The formatted error message.

    Raises:
        Exception: If an error occurs while logging the error message.
    """
    try:
        lineNum = str(sys.exc_info()[-1].tb_lineno)
        erType, erCause = str(type(args[0]).__name__), str(args[0])
        time = str(datetime.now())[:19]
        erStr = f'[{time}] \r\n- Err in module - {args[1]} on line {lineNum} | {erType} | {erCause}\r\n'

        if len(args) == 3:
            print(erStr)

        return erStr
    except Exception as e:
        print(f'Error: {e}')