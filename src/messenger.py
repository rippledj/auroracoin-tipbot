# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: SQL Abstraction Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package abstracts the web API connection details.  Profiles for connecting to sources can be created here. 
# The profile name is passed into the object upon creation. 

# Import Basic Python Modules
from email.mime.text import MIMEText
import datetime
import smtplib
import logging
# Import Aurtip package modules

class Messenger:
    # Define class variables for smtp server
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "auroracoin.wallet@gmail.com"
    SMTP_PASSWORD = "Auroranode"
    EMAIL_FROM = "auroracoin.wallet@gmail.com"
    EMAIL_SUBJECT = "+Aurtip response"
    def __init__(self, messages, api, db):
        # Create dictionary object
        import dictionary
        dictionary = dictionary.Dictionary("english")
        # Import logger and define instance variables
        self.log = logging.getLogger('__Aurtip__')
        self.log.debug("--Messenger Script Started--")
        self.messages = messages.messages
        message_text = ""
        # Build messages from the message payload
        first_time = True
        num_messages = len(self.messages)
        count = 0
        for message in self.messages:
            count += 1
            # first time store the
            if first_time == True:
                first_time = False
                previous_response_thread_id = message[0]
                previous_response_username = message[1]
                previous_response_destination = message[2]
                message_text = "Dear, " + message[1] + "\n"
            # If the message is directed to same thread_id and username as previous
            if message[0] == previous_response_thread_id and message[1] == previous_response_username and message[2] == previous_response_destination:
                previous_response_thread_id = message[0]
                previous_response_username = message[1]
                previous_response_destination = message[2]
                # append message text 
                message_text += message[3] + "\n"
            # If next item is directed to different thread_id or username
            else:
                # Append the message footer
                message_text += dictionary.MESSAGES_BOTTOM_LINE
                # Check the method to send the message and send it
                if previous_response_destination == "public":
                    print "---Forum Message---"
                    print message_text
                    publish_post = requests.post(api.new_post_url + "&parent_id=" +  message["thread_id"] + "&message=" + message_text)
                elif previous_response_destination == "private":
                    print "---Email Message---"
                    print message_text
                    #self.send_mail(message[1], message_text, db)
                # refresh the message thread_id and attach new text
                previous_response_thread_id = message[0]
                previous_response_username = message[1]
                previous_response_destination = message[2]
                message_text = "Dear, " + message[1] + "\n" + message[3] + "\n"
            if count == num_messages:
                message_text += dictionary.MESSAGES_BOTTOM_LINE
                if message[2] == "public":
                    print "---Forum Message---"
                    print message_text
                    #publish_post = requests.get(api.publish_url + "&thread_id" +  message["thread_id"] + "&message=" + message_text)
                elif message[2] == "private":
                    print "---Email Message---"
                    print message_text
                    #self.send_mail(message[1], message_text, db)
                
                
    def send_mail(self, username, message_text, db):
        email_to = db.get_user_email(username)
        self.log.debug("Email sent to user %s" % username)
        msg = MIMEText(message_text)
        msg['Subject'] = Messenger.EMAIL_SUBJECT
        msg['To'] = "joseph.lee.esl@gmail.com"
        msg['From'] = Messenger.EMAIL_FROM
        mail = smtplib.SMTP(Messenger.SMTP_SERVER, Messenger.SMTP_PORT)
        mail.starttls()
        mail.login(Messenger.SMTP_USERNAME, Messenger.SMTP_PASSWORD)
        mail.sendmail(Messenger.EMAIL_FROM, "joseph.lee.esl@gmail.com", msg.as_string())
        mail.quit()
