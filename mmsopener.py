"""
mmsopener.py
Stateful opener class for MMS requests. Keeps track of cookies so subsequent requests can be made.

sf37 - 31/12/2011
Part of the MMSpider project.
"""

import urllib2
import urllib
from cookielib import CookieJar
import cookielib
import mmsparser

NLI_TEXT = "University of St Andrews SSO" # text present when a log in is required
INCORRECT_TEXT = "cannot be determined to be authentic"
BASE_LOGIN_URL = "https://login.st-andrews.ac.uk"
#BASE_LOGIN_URL = "https://login-test.st-andrews.ac.uk"

class mmsopener:
    __username = None
    __password = None
    __opener = None # internal opener through which all stateful requests are made
    logger = None
    
    def __init__(self, user, pwd, logger):
        self.__username = user
        self.__password = pwd
        self.logger = logger
        cj = CookieJar()
        self.__opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    def login(self, login_html):
        """Logs in using the given form HTML data."""
        page_data = mmsparser.parse_login(login_html)
        values = { "username" : self.__username, "password": self.__password, "lt" : page_data["lt"], "_eventId" : page_data["eventid"]}
        data = urllib.urlencode(values)
        response = self.__opener.open(BASE_LOGIN_URL + page_data["dest"], data)
        content = response.read()
        if (INCORRECT_TEXT in content):
            self.logger.error("Login failed")
            return False #login failed
        self.logger.info("Login success!")
        return True
    
    def request(self, url):
        """Requests a URL using the current opener. Will log in if not already / opener not made.
           Returns HTML from page."""
        self.logger.info("Requesting page " + url)
        response = self.__opener.open(url)
        content = response.read()
        
        if NLI_TEXT in content:
            self.logger.info("Login requested")
            if not self.login(content):
                raise RuntimeError("Incorrect username / password given")
            else:
                return self.request(url) # re-call the method, since we'll have logged in now
        else:
            return content
