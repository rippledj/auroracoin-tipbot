# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Payload Handler Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package processes the payloads build from API calls.  Each command call has a function which handles the storing of data, 
# RPC calls to the bitcoind core software, transferring funds, and messages the users.

# Import Basic Modules
import re
import bitcoinrpc
import logging
import dictionary
import decimal

COMMAND_LIST = ["history", "tip", "info", "accept", "reject", "withdraw", "noemail", "balance", "pool", "autowithdraw", "unregister"]

class PayloadProcessor:
    def __init__(self, payload, db, rpc, exchange):
        self.USD_rate = exchange.USD_rate
        self.messages = []
        self.rpc = rpc
        self.log = logging.getLogger('__Aurtip__')
        if len(payload) > 0:
            self.log.debug("---Payload has commands in it---")
            self.payloadProcessor(payload, db, rpc)
    
    def payloadProcessor(self, payload, db, rpc):
        self.log.debug("---Payload Processor Starting---") 
        for item in payload:
            self.registrationCheck("user", item, db, rpc)
            if len(item['commands']) > 0:
                self.log.debug("Parsing payload commands from post %s" % item['thread_id'])
                # process all explicit commands in payload
                for command in item['commands']:
                    if command in COMMAND_LIST:
                        if command == 'info':
                            #check if user email onfile
                            email = db.get_user_email(item['site'], item['username'])
                            if email is None:
                                self.log.debug("User info request found. No email on file for user %s in post %s" % (item['username'], item['thread_id']))
                                self.buildMessage("no-email", item['thread_id'], item['username'])
                            else:
                                self.log.debug("User info command request from user %s in post %s" % (item['username'], item['thread_id']))
                                # get user info from database                            
                                info = db.get_user_info(item['site'], item['username'])
                                self.buildMessage("info", item['thread_id'], item['username'], info)
                        elif command == 'history':
                            # check if user email is onfile
                            email = db.get_user_email(item['site'], item['username'])
                            if email is None:
                                self.log.debug("User info request found. No email on file for user %s in post %s" % (item['username'], item['thread_id']))
                                self.buildMessage("no-email", item['thread_id'], item['username'])
                            else:
                                self.log.debug("User history command request from user %s in post %s" % (item['username'], item['thread_id']))
                                #get user account transaction history and send to user inbox
                                history_object = db.get_user_history(item['site'], item["username"])
                                self.buildMessage("history", item['thread_id'], item['username'], history_object)
                        elif command == 'tip':
                            self.log.debug("Tip command request from user %s in post %s" % (item['username'], item['thread_id']))
                            self.payloadTip(item, db, rpc)
                        elif command == 'accept':
                            self.log.debug("User registration 'accept' command for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to automatically accept the funds
                            db.change_user_preference(item['site'], item['username'], "registered", 1)
                            deposit_address = db.get_user_deposit_address(item['username'])
                            self.buildMessage("register", item['thread_id'], item['username'], deposit_address)
                        elif command == 'reject':
                            self.payloadReject(item['username'], item['tip_id'])
                            self.buildMessage("reject", item['thread_id'], item['tip_id'])
                        elif command == 'withdraw':
                            self.log.debug("Withdraw command request from user %s in post %s" % (item['username'], item['thread_id'])) 
                            self.payloadWithdraw(item, db, rpc)
                        elif command == 'balance':
                            #check if user email onfile
                            email = db.get_user_email(item['site'], item['username'])
                            if email is None:
                                self.log.debug("User balance request found. No email on file for user %s in post %s" % (item['username'], item['thread_id']))
                                self.buildMessage("no-email", item['thread_id'], item['username'])
                            else:
                                self.log.debug("Balance command request from user %s in post %s" % (item['username'], item['thread_id']))
                                self.buildMessage("balance", item['thread_id'], item['username'], db.get_balance(item['username']))
                        elif command == 'pool':
                            self.log.debug("Preference change request found: 'pool' for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to pool funds and not send tip right away
                            db.change_user_preference(item['site'], item['username'], "pool", 1)
                            self.buildMessage("preference", item['thread_id'], item['username'], "Now pooling tips")
                        elif command == 'autowithdraw':
                            self.log.debug("Preference change request found: 'autowithdraw' for user %s in post %s" % (item['username'], item['thread_id']))
                            # change user preference to automatically transfer tip funds to pubkey address
                            if db.change_user_preference(item['site'], item['username'], "pool", 0) == True:
                                self.buildMessage("preference", item['thread_id'], item['username'], "Now automatically withdrawing tips.")
                            else: 
                                self.buildMessage("autowd-no-address-error", item['thread_id'], item['username'])
                        elif command == 'noemail':
                            self.log.debug("Preference change request found: 'noemail' for user %s in post %s" % (item['username'], item['thread_id']))
                            # remove user email from our database
                            db.remove_user_email(item['site'], item['username'])
                            self.buildMessage("preference", item['thread_id'], item['username'], "Your email address has been removed from records.")
                        elif command == 'unregister':
                            db.unregister_user(item['site'], item['username'], item['datetime'], item['thread_id'])
                            self.buildMessage("unregister", item['thread_id'], item['username'])
                    else:
                        self.log.debug("Invalid command: '%s' included in post from user %s in post %s" % (command, item['username'], item['thread_id']))
                        #self.buildMessage("error", item['username'], command)
            elif len(item['recipient']) > 0 or len(item['amount']) > 0:
                self.payloadTip(item, db, rpc)
            elif "address" in item:
                self.log.debug("Change of public receive address requested for %s in post %s" % (item['username'], item['thread_id']))
                db.change_user_receive_address(item['site'], item["username"], item['address'])
                self.buildMessage("address-change", item['thread_id'], item['username'], item['address'])
            elif "email" in item:
                self.log.debug("Change of email address requested for %s in post %s" % (item['username'], item['thread_id']))
                db.change_user_email_address(item['site'], item["username"], item['email'])
                self.buildMessage("email-change", item['thread_id'], item['username'])
            
    def payloadWithdraw(self, item, db, rpc, address=None):
        withdraw_error = False
        # check that the amount is included
        if 'amount' in item:
            if len(item['amount']) != 1:
                withdraw_error = True
                self.log.debug("Incorrect number of amounts included in withdraw command for user %s in post %s" % (item['username'], item['thread_id']))
            else:
                balance = db.get_balance(item['site'], item['username'])
                amount_decimal = decimal.Decimal(item['amount'][0])
                balance_decimal = decimal.Decimal(balance)
                if amount_decimal > balance_decimal:
                    self.log.debug("Insufficient Funds for withdrawl in post %s" % (item['thread_id']))
                    data = (item['amount'][0], balance)
                    self.buildMessage("insufficient-withdraw", item['thread_id'], item['username'], data)
                    withdraw_error = True
        else:
            self.log.debug("No amount included in withdraw command from user %s in post %s" % (item['username'], item['thread_id']))
            withdraw_error = True
        # check that address is included
        if 'address' in item is None: 
            address = db.get_user_receive_address(item['site'], item['username'])
            if address is None:
                self.buildMessage("no address", item['thread_id'], item['username'])
                self.log.debug("No address is available for user %s" % (item['username']))
                withdraw_error = True
        else:
            address = item['address']
        # TODO: need a better address validation at this point
        if re.match(r"^[aA][a-km-zA-HJ-NP-Z0-9]{26,33}$", address):
            pass
        else: 
            withdraw_error = True
            self.log.debug("Address is not a valid Auroracoin address %s" % (address))
        #do transaction or create error message
        if withdraw_error == False:
            # check back pool balance to make sure there is enough
            back_pool_balance = rpc.bitcoin.getbalance("back_pool")
            back_pool_balance_decimal = decimal.Decimal(back_pool_balance)
            if back_pool_balance_decimal > amount_decimal:
                data = [item['amount'][0], address , balance]
                withdraw_txid = rpc.bitcoin.sendfrom("back_pool", address, amount_decimal)
                # add withdrawl to the database table
                db.withdraw_to_user(item['thread_id'], item['site'], item['username'], address, amount_decimal, withdraw_txid)
                self.buildMessage("withdraw", item['thread_id'], item['username'], data)
                self.log.critical("Withdrawl completed for %s \tAmount: %s \tAddress: %s" % (item['username'], item['amount'][0], address))
            else:
                # admin should be notified immedietly after this happens!
                self.buildMessage("error-admin", item['thread_id'], "Aurtip", item)
                self.buildMessage("error-back-pool-account", item['thread_id'], item['username'])
                self.log.critical("Insufficient funds in back_pool to complete withdrawl")
                
    def payloadAutoWithdraw(self, recipient, db, item):
        pass
    
    def payloadReject(self, username, unique_id=None):
        if unique_id is None:
            self.log.debug("No Tip ID available in reject request for %s" % username)
        else:
            self.log.debug("Processing a reject payment for %s and unique_id: %s" % (username, unique_id))
            if db.check_tip_status(username, unique_id) == True:
                # mark tip as rejected
                db.reject_tip(unique_id)
                self.log.debug("Tip %s rejected  for %s", (unique_id, username))
            else:
                self.log.debug("Tip %s has already been accepted, rejected, or withdrawn for %s" % (unique_id, username))
            
    def payloadTip(self, item, db, rpc):
        # checking amounts and addresses are appropirate in number
        if len(item['recipient']) != len(item['amount']) or len(item['recipient']) != 1 or len(item['amount']) != 1:
            self.log.debug("Wrong number of recipients or amounts in post %s" % item['thread_id'])
            #append info to error message
            self.buildMessage("error-tip-command-conflict", item['thread_id'], item['username'])
        else:
            amount = decimal.Decimal(item['amount'][0])
            if amount * self.USD_rate > 10:
                self.log.debug("Tip is higher than limit of $10 USD" % item['thread_id'])
                #append info to error message
                self.buildMessage("error-max-tip-exceeded", item['thread_id'], item['username'])
            else:    
                self.log.debug("Recipient and amount are OK in post %s" % item['thread_id'])
                recipient =  item['recipient'][0].replace("@", "")
                self.registrationCheck("recipient", item, db, rpc, recipient)
                # check balance is available for tip
                balance = db.get_balance(item['site'], item['username'])
                balance_decimal = decimal.Decimal(balance)
                amount = decimal.Decimal(item['amount'][0])
                if balance_decimal < amount:
                    self.log.debug("User balance %s insufficient for tip amount %s in post %s" % (balance, item['amount'][0], item['thread_id']))
                    self.buildMessage("insufficient-tip", item['thread_id'], item['username'], (item['amount'][0], balance))
                else:
                    # build a tip object
                    tip = [item['username'], recipient, item['amount'][0], item['thread_id'], item['datetime']]
                    # remove amount from sender balance
                    db.adjust_sender_balance(item['username'], item['amount'][0])
                    # get user tip preferences from database
                    tip_preferences = db.get_user_tip_preferences(recipient)
                    # if auto withdraw is user pref
                    if tip_preferences[0] == False:
                        db.store_tip("withdrawn", tip)
                        self.payloadAutoWithdraw(recipient, db, item)
                        self.log.debug("Tip has been autowithdrawn in post %s" % (item['thread_id']))
                        # withdraw to public address of user
                        # build messages
                        self.buildMessage("tip-sender-autoac", item['thread_id'], item['username'], tip)
                        self.buildMessage("tip-recipient-autowd", item['thread_id'], recipient , tip)
                    # if user registeration verified
                    elif tip_preferences[1] == True:
                        db.store_tip("accepted", tip)
                        db.adjust_recipient_balance(recipient, amount)
                        # for normal tips for verified users tips
                        self.log.debug("Tip accepted and stored in database for post %s" % (item['thread_id']))
                        # build messages
                        self.buildMessage("tip-sender-autoac", item['thread_id'], item['username'], tip)
                        self.buildMessage("tip-recipient-registered", item['thread_id'], recipient, tip)
                    # if user registration is not verified
                    else:
                        db.store_tip("none", tip)
                        self.log.debug("Tip stored in database, waiting for accept for post %s" % (item['thread_id']))
                        # build messages
                        self.buildMessage("tip-sender", item['thread_id'], item['username'], tip)
                        self.buildMessage("tip-recipient-unregistered", item['thread_id'], recipient, tip)
    
    def registrationCheck(self, type, item, db, rpc, recipient=None):
        if type == "user":
            # check if user is in the database already
            if db.check_user_in_database(item['site'], item['username']) == False:
                self.log.debug("Registration check - user is NOT in database already!")
                # register user, create deposit address and message user
                db.register_new_user("user", item)
                deposit_address = rpc.bitcoin.getnewaddress("deposit_pool")
                db.store_new_deposit_address(item['site'], item['username'], deposit_address)
                self.buildMessage("register", item['thread_id'], item['username'], deposit_address)
                self.log.debug("New user registered: %s in post %s" % (item['username'], item['thread_id']))
            # if in database already 
            else:
                self.log.debug("Registration check - user is in database already!")
                # if user is registered only as a recipient but not explicitly
                if db.check_user_registration_status(item['site'], item['username']) == False:
                    # change user preference to automatically accept the funds
                    db.change_user_preference(item['site'], item['username'], "registered", 1)
                    # move all pending tips to the balance for user
                    db.accept_pending_tips(item['site'], item['username'])
                    deposit_address = db.get_user_deposit_address(item['site'], item['username'])
                    self.buildMessage("register", item['thread_id'], item['username'], deposit_address)
                    self.log.debug("Previous recipeint registered: %s in post %s" % (item['username'], item['thread_id']))
        if type == "recipient":
            if db.check_user_in_database(item['site'], recipient) == False:
                    db.register_new_user("recipient", item, recipient)
                    deposit_address = rpc.bitcoin.getnewaddress("deposit_pool")
                    db.store_new_deposit_address(item['site'], recipient, deposit_address)
                    self.buildMessage("register-recipient", item['thread_id'], item['username'], deposit_address)
                    self.log.debug("Recipient entered into databse: %s in post %s" % (recipient, item['thread_id']))
                    
    def buildMessage(self, type, thread_id, recipient, data=None):
        # array to hold all messages
        import dictionary
        dictionary = dictionary.Dictionary("english")
        if type == "info":
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_INFO))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_USERNAME + data[4]))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_EMAIL_ADDRESS + data[5]))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_REGISTRATION_DATE + str(data[0])))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_BALANCE + data[2] + " AUR"))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_DEPOSIT_ADDRESS + data[6]))
            if data[1] is None:
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_RECEIVE_PUBKEY +  " None"))
            else:
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_RECEIVE_PUBKEY + data[1]))
            if data[3] == True:
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_AUTO_WITHDRAW + " True"))
            else:
                self.messages.append((thread_id, recipient, "private",  dictionary.MESSAGES_AUTO_WITHDRAW + "False"))
        if type == "balance":
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_BALANCE + data + " AUR"))
        if type == "history":
            if data is None:
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_HISTORY))
            else:
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_HISTORY))
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_PENDING_HISORY))
                if len(data[0]) == 0:
                    self.messages.append((thread_id, recipient, "private", "none"))
                else:
                    for item in data[0]:
                        self.messages.append((thread_id, recipient, "private", str(item['id']) + "_A" + "\t" + str(item['datetime']) + "\t" + item['amount'] + "\t" + item['sender_username']))
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_WITHDRAW_HISTORY))
                if len(data[1]) == 0:
                    self.messages.append((thread_id, recipient, "private", "none"))
                else:
                    for item in data[1]:
                        self.messages.append((thread_id, recipient, "private", str(item['datetime']) + "\t" + item['amount'] + " AUR" + "\t" + item['receive_pubkey']))
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_DEPOSIT_HISTORY))
                if len(data[2]) == 0:
                    self.messages.append((thread_id, recipient, "private", "none"))
                else:
                    for item in data[2]:
                        self.messages.append((thread_id, recipient, "private", str(item['datetime']) + "\t" + item['amount'] + " AUR"))
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_TIP_RECEIVED_HISTORY))
                if len(data[3]) == 0:
                    self.messages.append((thread_id, recipient, "private", "none"))
                else:
                    for item in data[3]:
                        self.messages.append((thread_id, recipient, "private", str(item['id']) + "_A" + "\t" + str(item['datetime']) + "\t" + item['amount'] + "\t" + item['receive_username']))
                self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ACCOUNT_TIP_SENT_HISORY))
                if len(data[4]) == 0:
                    self.messages.append((thread_id, recipient, "private", "none"))
                else:
                    for item in data[4]:
                        self.messages.append((thread_id, recipient, "private", str(item['id']) + "_A" + "\t" + str(item['datetime']) + "\t" + item['amount'] + "\t" + item['sender_username']))
                
        if type == "tip-sender":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_SENDER + data[1]))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_AMOUNT + str(data[2]) + " AUR"))
        if type == "tip-sender-autoac":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_SENDER_AUTOAC + data[1]))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_AMOUNT + str(data[2]) + " AUR"))
        if type == "tip-recipient-unregistered":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_RECIPIENT + data[0]))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_AMOUNT + str(data[2]) + " AUR"))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_REGISTRATION_INSTRUCTIONS))
        if type == "tip-recipient-autowd":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_RECIPIENT_AUTOWD))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_AMOUNT + str(data[2]) + " AUR"))
        if type == "tip-recipient-registered":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_RECIPIENT_AUTOAC + data[0]))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_AMOUNT + str(data[2]) + " AUR"))
        if type == "reject":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_TIP_REJECT))
        if type == "withdraw":
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_WITHDRAW))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_AMOUNT + data[0] + " AUR"))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_PUBKEY + data[1]))
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_BALANCE + data[2] + " AUR"))
        if type == "preference":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_PREFERENCE + data))
        if type == "register":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_REGISTER))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_REGISTRATION_DEPOSIT_ADDRESS + data))
        if type == "error":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_ERROR + data))
        if type == "error-tip-commands-conflict":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_ERROR_TIP_COMMAND_CONFLICT))
        if type == "error-back-pool-account":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_BACK_POOL_ERROR))
        if type == "error-max-tip-exceeded":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_MAX_TIP_EXCEEDED))
        if type == "no-email":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_NO_EMAIL))
        if type == "insufficient-tip":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_INSUFFICIENT_TIP + str(data[0])))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_INSUFFICIENT_BALANCE + str(data[1]) + " AUR"))
        if type == "insufficient-withdraw":
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_INSUFFICIENT_WITHDRAW + str(data[0])))
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_INSUFFICIENT_BALANCE + str(data[1]) + " AUR"))
        if type == 'email-change':
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_EMAIL_CHANGE))
        if type == 'address-change':
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ADDRESS_CHANGE + data))
        if type == 'autowd-no-address-error':
            self.messages.append((thread_id, recipient, "public", dictionary.MESSAGES_PREFERENCES_CHANGE_ERROR + dictionary.MESSAGES_NO_ADDRESS_ERROR))
        if type == 'error-admin':
            self.messages.append((thread_id, recipient, "private", dictionary.MESSAGES_ADMIN_ERROR + data['thread_id']))