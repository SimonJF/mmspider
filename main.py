#!/usr/bin/env python
import logging
import mmsopener
import mmsparser
import sys
import os.path
import smtplib

"""
                  ____                    __                  
 /'\_/`\  /'\_/`\/\  _`\           __    /\ \                 
/\      \/\      \ \,\L\_\  _____ /\_\   \_\ \     __   _ __  
\ \ \__\ \ \ \__\ \/_\__ \ /\ '__`\/\ \  /'_` \  /'__`\/\`'__\
 \ \ \_/\ \ \ \_/\ \/\ \L\ \ \ \L\ \ \ \/\ \L\ \/\  __/\ \ \/ 
  \ \_\\ \_\ \_\\ \_\ `\____\ \ ,__/\ \_\ \___,_\ \____\\ \_\ 
   \/_/ \/_/\/_/ \/_/\/_____/\ \ \/  \/_/\/__,_ /\/____/ \/_/ 
                              \ \_\                           
                               \/_/                           

MMS Spider Application - allows for automated crawling of MMS coursework pages to 
check to see whether the coursework grades have been changed or updated.

Written 31/12/2011 by Simon Fowler <sf37@st-andrews.ac.uk>

"""

# Constants
LOGGER_NAME = "mmspider"
LOGGER_LEVEL = logging.INFO
MMS_URL = "https://mms.st-andrews.ac.uk/mms/user/me/Modules"
CHANGED_SUBJECT = "MMSpider Alert: Change in Module Grades"

def get_logger(name, level):
    """Returns a standard logger with the given name and level"""
    logger = logging.getLogger(name)
    filehandler = logging.FileHandler(name + ".log")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -   %(message)s")
    filehandler.setFormatter(formatter)
    filehandler.setLevel(level)
    logger.addHandler(filehandler)
    return logger
    
def send_mail(msg_from, msg_to, msg_subject, msg_body):
    """Sends an e-mail with the given parameters"""
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (msg_from, msg_to, msg_subject)) + msg_body
    s = smtplib.SMTP('localhost')
    s.sendmail(msg_from, [msg_to], msg)
    s.quit()

    
def process_cwk_page(name, url, opener, logger):
    """Processes a coursework URL, checks to see whether a notification needs to be sent or not and returns
       a tuple of (notification required :: Bool, serialised grade data :: String)"""
    filename = name + ".txt"
    html = opener.request(url)
    info = mmsparser.parse_cwk_list(html)
    cwk_str = ""
    notify = True
    
    for entry in info:
        cwk_str = cwk_str + "Name: " + entry["name"] + ", Grade: " + entry["grade"] + ", Comments URL: " + url + entry["comments_url"] + "\n" 
        
    # if a comparison file exists, check for changes
    if os.path.exists(filename):
        comp_file = open(filename, "r")
        comp_str = comp_file.read()
        comp_file.close()
        if cwk_str == comp_str: # no change
            logger.info("No change.")
            return (False, None) # nothing doing
    else:
        notify = False # so we don't notify the user unnecessarily, considering this is first run
    
            
    # if a comparison file doesn't exist, create a new file or update the file and notify the user
    logger.info("Creating / Updating the comparison file " + filename)
    
    comp_file = open(filename, "w")
    comp_file.write(cwk_str)
    comp_file.close()
    return (notify, cwk_str)
    
if __name__ == "__main__":
    logger = get_logger(LOGGER_NAME, LOGGER_LEVEL)
    
    if (len(sys.argv) < 3): # log and error out if we don't have the correct credentials
        logger.error("Incorrect syntax given: username, password and email must be given as arguments")
        quit(-1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3]
    opener = mmsopener.mmsopener(username, password, logger)
    modules_html = None
    try:
        modules_html = opener.request(MMS_URL)
    except RuntimeError:
        logger.error("Username or password incorrect.")
        quit(-1)
        
    # parse module html
    modules = mmsparser.parse_modules_list(modules_html)
    
    # parse each module in turn
    for name, url in modules.items():
        (notify, data) = process_cwk_page(name, url, opener, logger)
        if notify:
            body = "There has been a change in module grades for the module " + name + ". These are detailed below.\n\n" + data
            send_mail(email, email, CHANGED_SUBJECT, body)   
