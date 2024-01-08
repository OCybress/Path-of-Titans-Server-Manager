import os
import sys
from datetime import datetime

def error(*args):
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