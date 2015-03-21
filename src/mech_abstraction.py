# -*- coding: utf-8 -*-
# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: API Abstraction Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package abstracts the web API connection details.  Profiles for connecting to sources can be created here. 
# The profile name is passed into the object upon creation. 

# Import Basic Modules
import cookielib 
import urllib2 
import mechanize
import time
import logging

class Mechanizer:
    def __init__(self):
        # Import logger
        self.log = logging.getLogger('__Aurtip__')
        # Browser 
        self.br = mechanize.Browser() 
        # Enable cookie support for urllib2 
        self.cookiejar = cookielib.LWPCookieJar() 
        self.br.set_cookiejar(self.cookiejar) 

        # Browser options 
        self.br.set_handle_equiv(True) 
        self.br.set_handle_gzip(True) 
        self.br.set_handle_redirect(True) 
        self.br.set_handle_referer(True) 
        self.br.set_handle_robots(False) 
        self.br.set_handle_refresh( mechanize._http.HTTPRefreshProcessor(), max_time = 1 ) 
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')] 
        self.log.debug("")
        
    def authenticate(self, login_url, username, password, profile_type):
        # authenticate 
        self.br.open(login_url) 
        try: 
            self.br.select_form(nr=1)
        except Exception:
            self.br.select_form(nr=0)
        self.br.form["username"] = username
        self.br.form["password"] = password
        self.br.method = "POST"
        response = self.br.submit()
        self.log.debug("---Authentication Script Finished for %s ---" % username)

    def post(self, post_url, forum, thread, message, profile_type):
        self.br.open(post_url + '&f=' + forum + '&t=' + thread)
        self.br.select_form(nr=1)
        self.br.form["subject"] = "Aurtip Response"
        self.br.form["message"] = message
        self.br.method = "POST"
        time.sleep(5)
        self.br.submit(nr=2)
        self.log.debug("---Mechanizer Post Complete for forum: %s thread: %s ---" % (forum, thread))
        time.sleep(15)