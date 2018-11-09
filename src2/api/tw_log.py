import logging
import functools
import time
from random import randint
import datetime
import os
import atexit


# DEBUG: Detailed information that addresses problems diagnoses
# INFO: Confirmation that things are working as expected
# WARNING: Indication that something unexpected happened or may happen in the near future
# ERROR: Serious issue, some functions may be disabled
# CRITICAL: A serious error, indicating the program itself may be unable to continue running

log_filename = "tw_log.out"
logging.basicConfig(filename=log_filename, level=logging.DEBUG) 
levels = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

def log(_level: str, _log: str) -> None:
    if _level == "debug":
        logging.DEBUG(_log)
        return
    
    elif _level == "info":
        logging.INFO(_log)
        return
    
    elif _level == "warning":
        logging.WARNING(_log)
        return
    
    elif _level == "error":
        logging.ERROR(_log)
        return
    
    elif _level == "critical":
        logging.CRITICAL(_log)
        return
    
    else:
        return


def action_log(input:str):
    with open("tw_log.txt", "a") as file:
        init_line = str(datetime.datetime.now().strftime("[%H:%M:%S] "))
        endline = "\n"
        file.write(init_line + input + endline)
        file.close()
        

