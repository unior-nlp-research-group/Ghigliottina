# -*- coding: utf-8 -*-
import logging
import traceback

def exception_reporter(func):    
    def dec(*args):
        try:
            func(*args)
        except Exception:
            from telegram_bot import report_master
            report_string = '❗️ Exception {}'.format(traceback.format_exc()) #.splitlines()
            logging.error(report_string)          
            try:  
                report_master(report_string)
            except Exception:
                report_string = '❗️ Exception {}'.format(traceback.format_exc())
                logging.error(report_string)          
    return dec

@exception_reporter
def myfunc():
    1/0

def test():
    myfunc()
