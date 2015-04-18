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

class ApiConnection:
    def __init__(self, profile, site=None):
        self.aurora_node_balance = "http://104.236.66.174:3333/chain/Auroracoin/q/addressbalance/"
        if profile == "test":
            self.api_type = "test"
            self.api_site = "test"
        # bland.is profile
        if profile == "bland":
            self.api_type = "bland"
            self.api_site = "bland"
            self.base_url = "https://api.bland.is/"
            key = "97c92bb0-350f-41df-b37f-788ca6ebda93"
            access_token= "bAkAIoYqNrIWiDZzz%2fKGrn80GwBpVdnSGhUdVxc9%2byXCWboKlHZaEnwd5SD2JRM%2bNttdAQJ1tD7RGrJsyaR3fNDOjQL9h2SE"
            # Bland.is requires three APIs for finding commands in user text
            self.new_post_url = self.base_url + "me/messageboard/?api_key=" + key + "&access_token=" + access_token
        
        if profile == "phpbb":
            if site == "auroraspjall":
                self.api_type = "phpbb"
                self.api_site = "auroraspjall"
                self.feed_url = "http://auroraspjall.is/feed.php"
                self.login_url = "http://auroraspjall.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://auroraspjall.is/posting.php?mode=reply&"
            if site == "jeppaspjall":
                self.api_type = "phpbb"
                self.api_site = "Hið íslenska jeppaspjall"
                self.feed_url = "http://www.jeppaspjall.is/feed.php"
                self.login_url = "http://www.jeppaspjall.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Aurora Node ##"
                self.post_url = "http://www.jeppaspjall.is/posting.php?mode=reply&"
            if site == "skyttur":
                self.api_type = "phpbb"
                self.api_site = "skyttur"
                self.feed_url = "http://spjall.skyttur.is/feed.php"
                self.login_url = "http://spjall.skyttur.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://spjall.skyttur.is/posting.php?mode=reply&"
            if site == "islandrover":
                self.api_type = "phpbb"
                self.api_site = "islandrover"
                self.feed_url = "http://www.islandrover.is/spjall/feed.php"
                self.login_url = "http://www.islandrover.is/spjall/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://www.islandrover.is/spjall/posting.php?mode=reply&"
            if site == "blyfotur":
                self.api_type = "phpbb"
                self.api_site = "blyfotur"
                self.feed_url = "http://spjall.blyfotur.is/feed.php"
                self.login_url = "http://spjall.blyfotur.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://spjall.blyfotur.is/posting.php?mode=reply&"
            if site == "kruser":
                self.api_type = "phpbb"
                self.api_site = "kruser"
                self.feed_url = "http://spjall.kruser.is/feed.php"
                self.login_url = "http://spjall.kruser.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://spjall.kruser.is/posting.php?mode=reply&"
            if site == "mbclub":
                self.api_type = "phpbb"
                self.api_site = "mbclub"
                self.feed_url = "http://mbclub.is/spjall/feed.php"
                self.login_url = "http://mbclub.is/login"
                self.username = "aurtip"
                self.password = "Auroranode##"
                self.post_url = "http://mbclub.is/posting.php?mode=reply&"


                
                