# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Get Payload Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package collects payloads from the web-API.  The payloads are a list in the class containing command information 
# The original class parses forum threads and inbox messages to our account.  The abstracted API is used to get the url.

# Import Basic Modules
import datetime
import logging
import requests
import re
import json
import bitcoinaddress

COMMAND_LIST = ["history", "tip", "info", "accept", "reject", "withdraw", "noemail", "balance", "pool", "autowithdraw", "unregister"]

class Payload:
    def __init__(self, payload_type, api, db):
        # initialize payload object which will hold all commands found
        self.payload = []
        self.log = logging.getLogger('__Aurtip__')
        self.log.debug("---Payload creation process started---")
        # Payload abstraction
        # you can define a payload type here. 
        # If can parse any API accessible text.
        # The text can be in json or text file.
        
        if payload_type == "bland" or payload_type == "phpbb":
            # create a list of payload information
            self.getForumPayload(api, db)
        if payload_type == "inbox":
            # create a list of payload information
            self.getMessagePayload(api, db)
        if payload_type == "test":
            self.getTestPayload(api, db)
        self.log.debug("---Payload creation process completed successfully---")
        
    def getForumPayload(self, api, db):
        if api.api_type == 'bland':
            # Paging constants
            LIMIT = 30
            offset = 0
            # TODO: WRAPPER to get previous paging if the last post is not on the page
            # API call to get the web-app forum
            category_response = requests.get(api.categories_url)
            if category_response.status_code == 200:
                self.log.debug("---Categories Received---")
                for item in json.loads(category_response.content):
                    offset = 0
                    last_post_found = False
                    first_new_post = True
                    # get the last date from database
                    try:    
                        last_post = db.get_last_post("bland", item["category_id"])
                    except Exception as e:
                        # initialize last_post to unmatchable
                        last_post = db.get_last_post("bland", 21)
                    last_post_created_datetime = datetime.datetime.strptime(str(last_post['created_datetime']), "%Y-%m-%d %H:%M:%S")
                    last_post_updated_datetime = datetime.datetime.strptime(str(last_post['updated_datetime']), "%Y-%m-%d %H:%M:%S")
                    self.log.debug("Category: %s - Last post [ID]: %s Created: %s Updated: %s" % (str(item["category_id"]), str(last_post['thread_id']), str(last_post_created_datetime), str(last_post_updated_datetime)))
                    # While last post not found
                    while last_post_found == False:
                        threads_update_response = requests.get(api.threads_url + str(item["category_id"]) + "&limit=" + str(LIMIT) + "&offset=" + str(offset))
                        if threads_update_response.status_code == 200:
                            threads = json.loads(threads_update_response.content)
                            for post in threads["data"]:
                                # Get time from post object
                                post_updated_time_raw = post["updated_time"].split()
                                post_date_list = post_updated_time_raw[0].split(".", 3)
                                post_time_list = post_updated_time_raw[1].split(":", 3)
                                post_updated_datetime = datetime.datetime(int(post_date_list[2]), int(post_date_list[1]), int(post_date_list[0]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
                                post_created_time_raw = post["created_time"].split()
                                post_date_list = post_created_time_raw[0].split(".", 3)
                                post_time_list = post_created_time_raw[1].split(":", 3)
                                post_created_datetime = datetime.datetime(int(post_date_list[2]), int(post_date_list[1]), int(post_date_list[0]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
                                #self.log.debug("---Last post created datetime: %s This post created datetime: %s" % (last_post_created_datetime, post_created_datetime))
                                #self.log.debug("---Last post updated datetime: %s This post updated datetime: %s" % (last_post_updated_datetime, post_updated_datetime))
                                # put new last post in database if it's first one found
                                if post_updated_datetime < last_post_updated_datetime or post_updated_datetime == last_post_updated_datetime:
                                    self.log.debug("Last post found: %s" % (str(last_post['thread_id'])))
                                    last_post_found = True
                                    break
                                elif first_new_post == True:
                                    self.log.debug("New Last Post Inserted to database: %s", (post['id']))
                                    db.insert_new_last_post("bland", item['category_id'], post['id'], post_created_datetime, post_updated_datetime)
                                    first_new_post = False
                                if post['updated_time'] == post['created_time']:
                                    # insert first post into database as last_post
                                    self.log.debug("Parsing new post: %s Posted at: %s %s  Page: %s" % (post["id"], str(post_created_datetime), str(post_updated_datetime), str(offset)))
                                    # prepare the post data to pass to parser
                                    prepared_post = {}
                                    prepared_post['username'] = post['from']['name']
                                    prepared_post['id'] = post['id']
                                    prepared_post['text'] = post['text']
                                    prepared_post['site'] = api.api_site
                                    # parse each thread for commands
                                    self.parseTextToPayload(prepared_post, str(post_created_datetime))
                                else: 
                                    self.log.debug("Skipping updated post: %s" % post['id'])
                            if last_post_found == False:
                                #increment the page variable.
                                offset += 1
        if api.api_type == 'phpbb':
            feed_response = requests.get(api.feed_url)
            if feed_response.status_code == 200:
                self.log.debug("---Feed.php Received---")
                # using feedparser to grab the xml feed from the phpbb site
                import feedparser
                first_entry = True
                last_post_found = False
                feed = feedparser.parse(feed_response.content)
                site_name = feed.feed.title
                # Get last post ID    
                try:    
                    last_post = db.get_last_post(site_name)
                except Exception as e:
                    # initialize last_post to unmatchable
                    last_post = db.get_last_post(site_name, 0)
                for entry in feed.entries:
                    prepared_post = {}
                    # Get updated and published times from post object and created datetime objects
                    post_updated_datetime_list = entry.updated.split("T", 2)
                    post_updated_date = post_updated_datetime_list[0]
                    post_updated_time_list = post_updated_datetime_list[1].split("+", 2)
                    post_updated_time = post_updated_time_list[0]
                    post_updated_datetime = datetime.datetime.strptime(post_updated_date + " " + post_updated_time, "%Y-%m-%d %H:%M:%S")
                    # get the post id
                    post_id_raw = entry.id.split("#", 2)
                    thread_id = entry.id.split("?", 2)[1].split("&", 2)[0].replace("t=", "")
                    forum_id =  entry['tags'][0]['scheme'].split("=", 2)[1]
                    # prepare entry data to pass to parser
                    prepared_post['post_id'] = post_id_raw[1].replace("p", "")
                    prepared_post['id'] = forum_id + "-" + thread_id + "-" + prepared_post['post_id']
                    prepared_post['site'] = site_name
                    prepared_post['username'] = entry.author
                    prepared_post['text'] = re.sub('<[^<]+?>', '', entry.content[0]['value']).replace("S", " ")
                    if hasattr(entry, "published"):
                        post_created_datetime_list = entry.published.split("T", 2)
                        post_created_date = post_created_datetime_list[0]
                        post_created_time_list = post_created_datetime_list[1].split("+", 2)
                        post_created_time = post_created_time_list[0]
                        post_created_datetime = post_created_date + " " + post_created_time
                        post_created_datetime = datetime.datetime.strptime(post_created_date + " " + post_created_time, "%Y-%m-%d %H:%M:%S")
                        # Enter new last post if new one found
                        if first_entry == True:
                            if last_post is None:
                                db.insert_new_last_post(api.api_site, forum_id, thread_id, prepared_post['post_id'], post_created_datetime, post_updated_datetime)
                                last_post = db.get_last_post(api.api_site)
                                self.log.debug("First Last Post for site: %s Post number: %s" % (site_name, prepared_post['post_id']))
                            elif int(prepared_post['post_id']) > int(last_post['post_id']):
                                db.insert_new_last_post(api.api_site, forum_id, thread_id, prepared_post['post_id'], post_created_datetime, post_updated_datetime)
                                self.log.debug("New Last Post Inserted to database: %s", (prepared_post['post_id']))
                            first_entry = False
                        # check if post should be parsed and parse
                        if post_updated_datetime == post_created_datetime and int(prepared_post['post_id']) > int(last_post['post_id']):
                            self.parseTextToPayload(prepared_post, str(post_created_datetime))
                        elif int(prepared_post['post_id']) == int(last_post['post_id']):
                            self.log.debug("Last post found: %s" % last_post['post_id'])
                            last_post_found = True
                        else: 
                            self.log.debug("Skipping previous post: %s" % prepared_post['post_id'])
                        # if last post is still not found in the feed
                        # need to go to each URL until finding last post
                    else:
                        if first_entry == True:
                            if last_post is None:
                                db.insert_new_last_post(api.api_site, forum_id, thread_id, prepared_post['post_id'], post_updated_datetime, post_updated_datetime)
                                last_post = db.get_last_post(api.api_site)
                                self.log.debug("First Last Post for site: %s Inserted to database: %s" % (site_name, prepared_post['post_id']))
                            elif int(prepared_post['post_id']) > int(last_post['thread_id']):
                                db.insert_new_last_post(api.api_site, forum_id, thread_id, prepared_post['post_id'], post_updated_datetime, post_updated_datetime)
                                self.log.debug("New Last Post Inserted to database: %s", (prepared_post['post_id']))
                            first_entry = False
                        # check if post should be parsed and parse
                        if int(prepared_post['post_id']) > int(last_post['post_id']):
                            self.parseTextToPayload(prepared_post, str(post_updated_datetime))
                        elif int(prepared_post['post_id']) == int(last_post['post_id']):
                            self.log.debug("Last post found: %s" % last_post['post_id'])
                            last_post_found = True
                        else:
                            self.log.debug("Skipping previous post: %s" % prepared_post['post_id'])
                        # if last post is still not found in the feed
                        # need to go to each URL until finding last post
            else:
                print feed_response.status_code
                print feed_response.content
                self.log.debug("---Feed Not Available---")
        
    def getMessagePayload(self, api, db):
        # API call to get web-app messages
        info_response = requests.get(api.info_url)
        if info_response.status_code == 200:
            info = json.loads(info_response.content)
            print "New Messages: " + str(info["new_messages_count"])
            if info['new_messages_count'] > 0:
                inbox_response = requests.get(api.inbox_url + "3")
                if inbox_response.status_code == 200:
                    print "Inbox Retreived"
                    inbox = json.loads(inbox_response.content)
                    print inbox['count'] + " messages in inbox" 
                    print inbox
                    # self.parseTextToPayload(text)
    
    def parseTextToPayload(self, post, post_datetime):
        command_found = False
        command_valid = False
        # look for REGEX for +AURtip and take it plus next three expressions.
        print post['text']
        if re.findall(r"(^|\s)[\+][aA][uU][rR][tT][iI][pP](\s|$)", post['text']):
            self.log.debug("AURtip Command Found in post: %s %s"% (post['id'], post['username']))
            # Make a list of strings to be used in the command parse.  Maybe more than one command per post.
            regex_commands = re.findall(r"([\+][aA][uU][rR][tT][iI][pP]($|[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}|[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}[\s][\@]?[0-9a-zA-Z\.\@\_]{1,}|[\s][0-9a-zA-Z\.\@\_]{1,}|[\s]))", post['text'])
            for command in regex_commands:
                payload_item = {}
                command_elements = command[0].split(" ", 4)
                self.log.debug(command_elements)
                command_list = []
                amount_list = []
                recipient_list = []
                for element in command_elements:
                    element = element.strip(".")
                    # if it's only a word it's a command
                    if re.findall(r"^[a-zA-Z]{1,12}$", element):
                        command = re.findall(r"^[a-zA-Z]{1,12}$", element)
                        if command[0] in COMMAND_LIST:
                            #print "Command: " + command[0]
                            command_list.append(command[0])
                    # if it has only numbers, or numbers and decimal
                    if re.findall(r"^[0-9]{1,6}\_[A]$", element):
                        tip_id = re.findall(r"^[0-9]{1,}\_[A]$", element)
                        #print "Tip ID: " + tip_id[0]
                        payload_item['tip_id'] = tip_id[0]
                    if re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element):
                        amount = re.findall(r"^[0-9]{1,6}\.?[0-9]{1,8}$", element)
                        #print "Amount: " + amount[0]
                        amount_list.append(amount[0])
                    # if it has '@' it is a username
                    if re.findall(r"[\@][0-9a-zA-Z]{1,}$", element):
                        username = re.findall(r"^[\@][0-9a-zA-Z]{1,}$", element)
                        #print "Username: " + username[0]
                        recipient_list.append(username[0])
                    # if it's a AuroraCoin address
                    if re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element):
                        address = re.findall(r"^[Aa][1-9A-HJ-NP-Za-km-z]{26,34}$", element)
                        #print "Address: " + address[0]
                        payload_item['address'] = address[0]
                    if re.findall(r"^[a-zA-Z0-9._]{1,}[\@][a-zA-Z0-9._]{1,}[\.][a-zA-Z]{3,}$", element):
                        email = re.findall(r"^[a-zA-Z0-9._]{1,}[\@][a-zA-Z0-9._]{1,}[\.][a-zA-Z]{3,}$", element)
                        #print "Email: " + email[0]
                        payload_item['email'] = email[0]
                payload_item['commands'] = command_list
                payload_item['recipient'] = recipient_list
                payload_item['amount'] = amount_list
                payload_item['site'] = post['site']
                payload_item['username'] = post['username']
                payload_item['thread_id'] = post['id']
                payload_item['datetime'] = post_datetime
                self.payload.append(payload_item)
                self.log.debug("Payload item created successfully: %s"%(post['id']))
        else:
            self.log.debug("No command found in this post: %s %s"%(post['id'], post['username']))
        
            
    def getTestPayload(self, api, db):
        # open test text file
        # json_data = open('test_json.txt', 'r')
        # test_data = json.loads(json_data)
        with open ("test_json.txt", "r") as myfile:
            data = myfile.read().replace('\n', '')
        self.log.debug("Json Data Received from file" )
        posts = json.loads(data)
        for post in posts['data']:
            # Get time from post object
            prepared_post = {}
            prepared_post['username'] = post['from']['name']
            prepared_post['id'] = post['id']
            prepared_post['text'] = post['text']
            prepared_post['site'] = api.api_site
            post_updated_time_raw = post["updated_time"].split()
            post_date_list = post_updated_time_raw[0].split(".", 3)
            post_time_list = post_updated_time_raw[1].split(":", 3)
            post_datetime = datetime.datetime(int(post_date_list[2]), int(post_date_list[1]), int(post_date_list[0]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
            self.parseTextToPayload(prepared_post, str(post_datetime))