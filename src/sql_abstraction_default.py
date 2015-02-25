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

# Import Basic Modules
import logging  
import datetime


class SqlConnection:
    def __init__(self, profile):
        self.log = logging.getLogger('__Aurtip__')
        if profile == "mysql":
            try:
                import MySQLdb
                import MySQLdb.cursors
                db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="mysqlusername", # your username
                      passwd="mysqlpassword", # your password
                      db="auroratip", # name of the data base
                      cursorclass=MySQLdb.cursors.DictCursor)
                db.autocommit(True)
                self.cur = db.cursor()
                self.log.debug("MySQL Database Connection Successful")
            except:
                self.log.debug("MySQL database error")
        if profile == 'psql':
            try:
                import psycopg2
                db = psycopg2.connect("dbname='auroratip' user='joseph'")
                db.autocommit(True)
                cur = db.cursor()
                self.log.debug("PSQL Database Connection Successful")
            except:
                self.log.debug("PSQL database error")
    
    def get_last_post(self, category):
        self.cur.execute("SELECT * FROM last_post WHERE category = %s ORDER BY id desc LIMIT 1", (category))
        last_post = self.cur.fetchone()
        return last_post
    
    def insert_new_last_post(self, category, thread_id, created_datetime, updated_datetime):
        self.cur.execute("INSERT INTO last_post (category, thread_id, created_datetime, updated_datetime) VALUES(%s, %s, %s, %s)", (category, thread_id, created_datetime, updated_datetime))

    def check_user_in_database(self, username):
        self.cur.execute("SELECT count(*) as registered FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()['registered']
    
    def check_user_registration_status(self, username):
        self.cur.execute("SELECT registered FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()['registered']
        
    def register_new_user(self, type, item, username=None):
        if type == "user":
            self.cur.execute("INSERT INTO user_data (username, regdate, balance, reg_thread_id, pool, registered) VALUES (%s, %s, 0, %s, 1, 1)", (item["username"], item['datetime'], item["thread_id"]))
        elif type == "recipient":
            self.cur.execute("INSERT INTO user_data (username, regdate, balance, reg_thread_id, pool, registered) VALUES (%s, %s, 0, %s, 1, 0)", (username, item['datetime'], item["thread_id"]))
        
    def get_user_info(self, username):
        info = []
        self.cur.execute("SELECT username, regdate, CAST(SUM(balance) AS CHAR), pubkey, pool FROM user_data WHERE username = %s", (username))
        db_info = self.cur.fetchone()
        self.cur.execute("SELECT deposit_pubkey FROM deposit_addresses WHERE username = %s", (username))
        db_deposit_pubkey = self.cur.fetchone()['deposit_pubkey']
        info.append(db_deposit_pubkey)
        return info
    
    def get_user_tip_preferences(self, username):
        tip_preferences = []
        self.cur.execute("SELECT pool FROM user_data WHERE username = %s", (username))
        tip_preferences.append(self.cur.fetchone()['pool'])
        self.cur.execute("SELECT registered FROM user_data WHERE username = %s", (username))
        tip_preferences.append(self.cur.fetchone()['registered'])
        return tip_preferences
    
    def change_user_preference(self, username, type, value):
        if type == "pool":
            if value == 1:
                self.cur.execute("UPDATE user_data SET pool = %s WHERE username = %s", (value, username))
            elif value == 0:
                # check that user has a pubkey onfile to withdraw to
                self.cur.execute("SELECT pubkey from user_data WHERE username = %s", (username))
                pubkey = self.cur.fetchone()['pubkey']
                if pubkey is None:
                    return False
                else:
                    self.cur.execute("UPDATE user_data SET pool = %s WHERE username = %s", (value, username))
                    return True
        if type == "registered":
            self.cur.execute("UPDATE user_data SET registered = %s WHERE username = %s", (value, username))
            
    def get_user_history(self, username):
        history_object = []
        withdrawls = []
        deposits = []
        received = []
        sent = []
        pending = []
        self.cur.execute("SELECT id, CAST(amount AS CHAR) as amount, sender_username, datetime FROM tip_transactions WHERE receive_username = %s AND withdrawn = 0 AND accepted = 0 AND rejected = 0 ORDER BY datetime desc", (username))
        for row in  self.cur.fetchall():
            pending.append(row)
        history_object.append(pending)
        self.cur.execute("SELECT  CAST(amount AS CHAR) as amount, receive_pubkey, datetime FROM withdrawls WHERE receive_username = %s ORDER BY datetime desc", (username))
        for row in  self.cur.fetchall():
            withdrawls.append(row)
        history_object.append(withdrawls)
        self.cur.execute("SELECT CAST(amount AS CHAR) as amount, datetime FROM deposits WHERE username = %s ORDER BY datetime desc", (username))
        for row in self.cur.fetchall():
            deposits.append(row)
        history_object.append(deposits)
        self.cur.execute("SELECT id, CAST(amount AS CHAR) as amount, receive_username, datetime  FROM tip_transactions WHERE sender_username = %s ORDER BY datetime desc", (username))
        for row in  self.cur.fetchall():
            received.append(row)
        history_object.append(received)
        self.cur.execute("SELECT id, CAST(amount AS CHAR) as amount, sender_username, datetime FROM tip_transactions WHERE receive_username = %s ORDER BY datetime desc", (username))
        for row in  self.cur.fetchall():
            sent.append(row)
        history_object.append(sent)
        #print history_object
        return history_object
    
    def get_user_receive_address(self, username):
        self.cur.execute("SELECT pubkey FROM user_data WHERE username = %s", (username))
        return self.cur.fetchone()[0]
    
    def store_tip(self, type, tip):
        if type == "withdrawn":
            self.cur.execute("INSERT INTO tip_transactions (thread_id, sender_username, receive_username, amount, datetime, accepted, withdrawn, rejected) VALUES (%s, %s, %s, %s, %s, 1, 1, 0)", (tip[3], tip[0], tip[1], tip[2], tip[4]))
        elif type == "accepted":
            self.cur.execute("INSERT INTO tip_transactions (thread_id, sender_username, receive_username, amount, datetime, accepted, withdrawn, rejected) VALUES (%s, %s, %s, %s, %s, 1, 0, 0)", (tip[3], tip[0], tip[1], tip[2], tip[4]))
        elif type == "rejected":
            self.cur.execute("INSERT INTO tip_transactions (thread_id, sender_username, receive_username, amount, datetime, accepted, withdrawn, rejected) VALUES (%s, %s, %s, %s, %s, 0, 0, 1)", (tip[3], tip[0], tip[1], tip[2], tip[4]))
        elif type == "none":
            self.cur.execute("INSERT INTO tip_transactions (thread_id, sender_username, receive_username, amount, datetime, accepted, withdrawn, rejected) VALUES (%s, %s, %s, %s, %s, 0, 0, 0)", (tip[3], tip[0], tip[1], tip[2], tip[4]))    
        
    def unregister_user(self, username, datetime, thread_id):
        self.cur.execute("INSERT INTO unregister_requests (userame, thread_id, datetime) VALUES (%s, %s, %s)", (username, recipient, thread_id))
        #Delete user info from user_data?
        
    def get_balance(self, username):
        self.cur.execute("SELECT CAST(SUM(balance) AS CHAR) as balance FROM user_data WHERE username = %s", username)
        return self.cur.fetchone()["balance"]
    
    def store_new_deposit_address(self, username, address):
        self.cur.execute("INSERT INTO deposit_addresses (username, deposit_pubkey, received_to_date) VALUES (%s, %s, 0)", (username, address))
    
    def get_deposit_address_list(self):
        self.cur.execute("SELECT a.username, deposit_pubkey, received_to_date FROM deposit_addresses a JOIN user_data as b ON a.username = b.username WHERE b.registered = 1")
        return self.cur.fetchall()
    
    def change_user_receive_address(self, username, address):
        self.cur.execute("UPDATE user_data SET pubkey = %s WHERE username = %s", (address, username))
        
    def change_user_email_address(self, username, email):
        self.cur.execute("UPDATE user_data SET email = %s WHERE username = %s", (email, username))    
        
    def check_tip_status(self, username, unique_id):
        # check tip recipient and id are acceptable
        db_tip_id = unique_id.split("_", 2) 
        self.cur.execute("SELECT amount FROM tip_transactions WHERE receive_username = %s and id = %s and accepted = 0 and withdrawn = 0 and rejected = 0", (username, db_tip_id[0]))
        if self.cur.fetchone() is None:
            return False
        else:
            return True
    
    def accept_pending_tips(self, username):
        tip_list = []
        # get all unaccepted tips in tip-transactions and move to newly registered user
        self.cur.execute("SELECT SUM(amount) as amount FROM tip_transactions WHERE receive_username = %s AND accepted = 0 AND withdrawn = 0 AND rejected = 0", (username))
        balance_to_move = self.cur.fetchone()['amount']
        self.cur.execute("UPDATE tip_transactions SET accepted = 1 WHERE receive_username = %s", username)
        self.cur.execute("UPDATE user_data SET balance = balance + %s WHERE username = %s", (balance_to_move, username))
        
    def reject_tip(self, unique_id):
        db_tip_id = unique_id.split("_", 2)
        self.cur.execute("SELECT sender_username, receive_username, amount FROM tip_transactions WHERE id = %s", db_tip_id[0])
        tip = self.cur.fetchone()
        self.cur.execute("UPDATE tip_transactions SET rejected = 1 WHERE id = %s", db_tip_id[0])
        
    def adjust_sender_balance(self, username, amount):
        self.cur.execute("UPDATE user_data SET balance = balance - %s WHERE username = %s", (amount, username))
    
    def adjust_recipient_balance(self, username, amount):
        self.cur.execute("UPDATE user_data SET balance = balance + %s WHERE username = %s", (amount, username))
    
    def adjust_user_balance(self, username, amount):
        self.cur.execute("UPDATE user_data SET balance = balance - %s WHERE username = %s", (amount, username))
        
    def deposit_to_user(self, username, amount, pubkey):
        datetime_now = str(datetime.datetime.now())
        self.cur.execute("UPDATE user_data SET balance = balance + %s WHERE username = %s", (amount, username))
        self.cur.execute("UPDATE deposit_addresses SET received_to_date = received_to_date + %s WHERE username = %s", (amount, username))
        self.cur.execute("INSERT INTO deposits (username, amount, datetime, pubkey) VALUES(%s, %s, %s, %s)", (username, amount, datetime_now, pubkey))
        
    def store_pool_transaction(self, amount, pubkey, tx_id):
        datetime_now = str(datetime.datetime.now())
        self.cur.execute("INSERT INTO pool_transactions (amount, pubkey, datetime, txid) VALUES(%s, %s, %s, %s)", (amount, pubkey, datetime_now, tx_id))
    
    def remove_user_email(self, username):
        self.cur.execute("UPDATE user_data SET email = NULL WHERE username = %s ", username)
        
    def withdraw_to_user(self, thread_id, username, address, amount, txid):
        datetime_now = str(datetime.datetime.now())
        self.cur.execute("UPDATE user_data SET balance = balance - %s WHERE username = %s", (amount, username))
        self.cur.execute("INSERT INTO withdrawls (thread_id, receive_username, receive_pubkey, amount, datetime, txid) VALUES (%s, %s, %s, %s, %s, %s)", (thread_id, username, address, amount, datetime_now, txid))
        
    def store_exchange_rate(self, first, second, price, datetime):
        self.cur.execute("INSERT INTO exchange_rate (firstcurrency, secondcurrency, rate, datetime) VALUES (%s, %s, %s, %s )", (first, second, price, datetime))
        
    def get_last_exchange_rate(self):
        self.cur.execute("SELECT rate FROM exchange_rate WHERE firstcurrency = 'BTC' AND secondcurrency = 'USD' ORDER BY datetime desc LIMIT 1")
        BTC_rate = self.cur.fetchone()['rate']
        self.cur.execute("SELECT rate FROM exchange_rate WHERE firstcurrency = 'AUR' AND secondcurrency = 'BTC' ORDER BY datetime desc LIMIT 1")
        AUR_rate = self.cur.fetchone()['rate']
        return AUR_rate * BTC_rate
    
    def get_user_email(self, username):
        self.cur.execute("SELECT email FROM user_data WHERE username = %s", username)
        return self.cur.fetchone()['email']
    
    def get_user_deposit_address(self, username):
        self.cur.execute("SELECT deposit_pubkey FROM deposit_addresses WHERE username = %s", username)
        return self.cur.fetchone()['deposit_pubkey']
