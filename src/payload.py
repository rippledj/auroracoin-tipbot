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
from bs4 import BeautifulSoup
import datetime
import logging
import requests
import re
import json
import bitcoinaddress

COMMAND_LIST = ["history", "tip", "info", "accept", "reject", "withdraw", "noemail", "balance", "pool", "autowithdraw", "unregister"]

class Payload:
    def __init__(self, payload_type, site, api, db):
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
            self.getTestPayload(site, api, db)
        self.log.debug("---Payload creation process completed successfully---")
        
    def getForumPayload(self, api, db):
        if api.api_type == 'bland':
            last_post_found = False
            i = 1
            # Get last post
            try:    
                last_post = db.get_last_post(api.api_type, 0)
                last_post_created_datetime = datetime.datetime.strptime(str(last_post['created_datetime']), "%Y-%m-%d %H:%M:%S")
                last_post_updated_datetime = datetime.datetime.strptime(str(last_post['updated_datetime']), "%Y-%m-%d %H:%M:%S")
                self.log.debug("Last post retrieved: 1_%s Created: %s Updated: %s" % (str(last_post['post_id']), str(last_post_created_datetime), str(last_post_updated_datetime)))
                last_post_in_db = True
            except Exception as e:
                import traceback, os.path
                top = traceback.extract_stack()[-1]
                print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
                print e
                # initialize last_post to unmatchable
                self.log.debug("---No Last Post Found in DB---")
                last_post_in_db = False
            # While last post not found
            while last_post_found == False:
                thread_content = requests.get(api.base_url + "1_" + str(last_post['post_id'] + i) + '/')
                post = json.loads(thread_content.content)
                i += 1
                if post == 0:
                    self.log.debug("---Last Post Found: %s---" % str(last_post['post_id'] + i - 1))
                    if i != 1:
                        db.insert_new_last_post(api.api_site, "0", "0", str(last_post['post_id'] + i - 1), post_created_datetime, post_updated_datetime)
                    last_post_found = True
                if last_post_found == False:
                    # Get time from post object
                    post_id = post['id'].split("_",2)[1]
                    post_updated_time_raw = post["updated_time"].split("T")
                    post_date_list = post_updated_time_raw[0].split("-")
                    post_time_list = post_updated_time_raw[1].split(":", 3)
                    post_time_list[2] = post_time_list[2].split(".", 2)[0]
                    post_updated_datetime = datetime.datetime(int(post_date_list[0]), int(post_date_list[1]), int(post_date_list[2]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2])) 
                    post_created_time_raw = post["created_time"].split("T")
                    post_date_list = post_created_time_raw[0].split("-")
                    post_time_list = post_created_time_raw[1].split(":", 3)
                    post_time_list[2] = post_time_list[2].split(".", 2)[0]
                    post_created_datetime = datetime.datetime(int(post_date_list[0]), int(post_date_list[1]), int(post_date_list[2]), int(post_time_list[0]), int(post_time_list[1]), int(post_time_list[2]))
                    if last_post_in_db == False:
                        #algo for finding most recent post to seed the db
                        pass
                    else:
                        self.log.debug("Parsing new post: %s Posted at: %s %s" % (post["id"], str(post_created_datetime), str(post_updated_datetime)))
                        # prepare the post data to pass to parser
                        prepared_post = {}
                        prepared_post['username'] = post['from']['name']
                        prepared_post['id'] = post['id']
                        prepared_post['text'] = post['text']
                        prepared_post['site'] = api.api_site
                        # parse each thread for commands
                        self.parseTextToPayload(prepared_post, str(post_created_datetime))
  
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
                    last_post = db.get_last_post(api.api_site)
                    self.log.debug("---Last Post: %s retreived from database---" % last_post['post_id'])
                except Exception as e:
                    # initialize last_post to unmatchable
                    last_post = db.get_last_post(api.api_site, 0)
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
                    try:
                        thread_id = entry.id.split("?", 2)[1].split("&", 2)[0].replace("t=", "")
                        forum_id =  entry['tags'][0]['scheme'].split("=", 2)[1]
                    except Exception as e:
                        break
                    # prepare entry data to pass to parser
                    prepared_post['post_id'] = post_id_raw[1].replace("p", "")
                    prepared_post['id'] = forum_id + "-" + thread_id + "-" + prepared_post['post_id']
                    prepared_post['site'] = site_name
                    prepared_post['username'] = entry.author
                    temp_text = re.sub('<br />', ' ', entry.content[0]['value'])
                    prepared_post['text'] = re.sub('<[^<]+?>', '', temp_text).replace("S", " ")
                    # remove block quoted text
                    soup = BeautifulSoup(prepared_post['text'])
                    for tag in soup.find_all('blockquote'):
                        tag.replaceWith('')
                    prepared_post['text'] = soup
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
                                self.log.debug("First Last Post for site: %s Inserted to database: %s" % (api.api_site, prepared_post['post_id']))
                            elif int(prepared_post['post_id']) > int(last_post['post_id']):
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
        self.log.debug("---Post sent to parsing function---")
        self.log.debug("%s" % post['text'])
        # look for REGEX for +AURtip and take it plus next three expressions.
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
                    if re.findall(r"^[0-9]{,6}?\.?[0-9]{1,8}$", element):
                        amount = re.findall(r"^[0-9]{,6}?\.?[0-9]{1,8}$", element)
                        print "Amount: " + amount[0]
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
        
            
    def getTestPayload(self, site, api, db):
        if site == "test":
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
        if site == "phpbb":
            with open ("test_phpbb.txt", "r") as myfile:
                data = myfile.read().replace('\n', '')
            self.log.debug("XML Data Received from file" )
            # using feedparser to grab the xml feed from the phpbb site
            import feedparser
            first_entry = True
            last_post_found = False
            feed = feedparser.parse(feed_response.content)
            site_name = feed.feed.title
            # Get last post ID    
            try:    
                last_post = db.get_last_post(api.api_site)
                self.log.debug("---Last Post: %s retreived from database---" % last_post['post_id'])
            except Exception as e:
                # initialize last_post to unmatchable
                last_post = db.get_last_post(api.api_site, 0)
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
                try:
                    thread_id = entry.id.split("?", 2)[1].split("&", 2)[0].replace("t=", "")
                    forum_id =  entry['tags'][0]['scheme'].split("=", 2)[1]
                except Exception as e:
                    break
                # prepare entry data to pass to parser
                prepared_post['post_id'] = post_id_raw[1].replace("p", "")
                prepared_post['id'] = forum_id + "-" + thread_id + "-" + prepared_post['post_id']
                prepared_post['site'] = site_name
                prepared_post['username'] = entry.author
                temp_text = re.sub('<br />', ' ', entry.content[0]['value'])
                temp_text = re.sub('<[^<]+?>', '', temp_text).replace("S", " ")
                # remove block quoted text
                prepared_post['text'] = temp_text.split('<blockquote><br />')[1]
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
                            self.log.debug("First Last Post for site: %s Inserted to database: %s" % (api.api_site, prepared_post['post_id']))
                        elif int(prepared_post['post_id']) > int(last_post['post_id']):
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