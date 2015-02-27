# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Main Bank Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package is monitoring public addresses for user deposits and modifying database balance amounts.
# Components such as SQL, RPC, and forum API are abstracted with concerns for modularity. The original version is written with postresql
# and bitcoind v 0.7.

import decimal
import logging

class BankPayload:
    def __init__(self, type, api, db, rpc):
        self.log = logging.getLogger('__Aurtip__')
        self.log.debug("---Deposit Processor Started---")
        DEPOSIT_POOL_ACCOUNT = "deposit_pool"
        BACK_POOL_ACCOUNT = "back_pool"
        FEE_AMOUNT = decimal.Decimal(0.001)
        total_deposit = 0
        balance_found = False
        deposits = []
        if type == 'bank':
            pass
        elif type == 'test':
            address_list = db.get_deposit_address_list()
            for address in address_list:
                self.log.debug("Inspecting address: %s", address['deposit_pubkey'])
                # rpc call to get recieved for each address and compare to received to date
                received_to_date_string = str('%.10g' % address['received_to_date']).strip() 
                total_received = decimal.Decimal(rpc.bitcoin.getreceivedbyaddress(address['deposit_pubkey']))
                total_received_string = str('%.10g' % total_received).strip() 
                deposit_amount = decimal.Decimal(total_received_string) - address['received_to_date']
                self.log.critical("Deposit amount: %s Site: %s Username: %s Deposit address: %s", str('%.10g' % deposit_amount).strip(), address['site'], address['username'], address['deposit_pubkey'])
                total_deposit += deposit_amount
                if deposit_amount > 0:
                    balance_found = True
                    deposits.append((address['deposit_pubkey'], deposit_amount))
                    # modify user balance amount and received to date amount in database
                    db.deposit_to_user(address['site'], address['username'], deposit_amount, address['deposit_pubkey'])
                    self.log.debug("Deposits found for %s user %s in address %s : %s" % (address['site'], address['username'], address['deposit_pubkey'], deposit_amount))
            if balance_found == True:
                self.log.debug("---Deposits are being moved to a pool---")
                back_pool_address = rpc.bitcoin.getnewaddress("back_pool")
                self.log.debug("New address created for back pool transfer: %s" % (back_pool_address))
                move_balance = rpc.bitcoin.getbalance(DEPOSIT_POOL_ACCOUNT)
                move_balance_string = str('%.10g' % move_balance).strip()
                print move_balance
                move_txid = rpc.bitcoin.sendfrom(DEPOSIT_POOL_ACCOUNT, back_pool_address, move_balance)
                self.log.critical("Pooling deposits moved to back_pool: %s %s" % (back_pool_address, move_balance_string))
                db.store_pool_transaction(move_balance_string, back_pool_address, move_txid)
                new_balance = rpc.bitcoin.getbalance(DEPOSIT_POOL_ACCOUNT)
                new_balance_string = str('%.10g' % new_balance).strip()
                self.log.critical("New deposit pool balance: %s" % (new_balance_string))