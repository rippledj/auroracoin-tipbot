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
            base_url = "https://api.bland.is/"
            key = "you api key"
            access_token= "your access token"
            # Bland.is requires three APIs for finding commands in user text
            self.categories_url = base_url + "messageboard/categories?api_key=" + key
            self.threads_url = base_url + "messageboard/?api_key=" + key + "&category_id="
            self.info_url = base_url + "me/info?access_token=" + access_token
            self.inbox_url = base_url + "me/message?access_token=" + access_token + "&limit="
            self.publish_url = base_url + "me/publishes?access_token=" + access_token
            self.new_post_url = base_url + "me/messageboard/?api_key=" + key + "&access_token=" + access_token
            self.parent_id_url = "&parent_id=" 
            self.message_url = "&message="
        
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
            if site == "skyttur":
                self.api_type = "phpbb"
                self.api_site = "skyttur"
                self.feed_url = "http://spjall.skyttur.is/feed.php"
                self.login_url = "http://spjall.skyttur.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
            if site == "islandrover":
                self.api_type = "phpbb"
                self.api_site = "islandrover"
                self.feed_url = "http://www.islandrover.is/spjall/feed.php"
                self.login_url = "http://www.islandrover.is/spjall/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
            if site == "blyfotur":
                self.api_type = "phpbb"
                self.api_site = "blyfotur"
                self.feed_url = "http://spjall.blyfotur.is/feed.php"
                self.login_url = "http://spjall.blyfotur.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
            if site == "kruser":
                self.api_type = "phpbb"
                self.api_site = "kruser"
                self.feed_url = "http://spjall.kruser.is/feed.php"
                self.login_url = "http://spjall.kruser.is/ucp.php?mode=login"
                self.username = "aurtip"
                self.password = "Auroranode##"
            if site == "mbclub":
                self.api_type = "phpbb"
                self.api_site = "mbclub"
                self.feed_url = "http://mbclub.is/spjall/feed.php"
                self.login_url = "http://mbclub.is/login"
                self.username = "aurtip"
                self.password = "Auroranode##"


                
                
