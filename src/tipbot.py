#!/usr/bin/python
# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: Main Tipbot Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package is for parsing a forum for command calls and processing payment function through Auroracoin or another crypto-currency.
# Components such as SQL, RPC, and forum API are abstracted with concerns for modularity. The original version is written with postresql
# and bitcoind v 0.7.

# Import Basic Modules
import requests
import bitcoinrpc
import logging
import sys

# Import tip-bot Modules
import payload
import payloadProcessor
import messenger
import exchangeRate
import bank

# Import abstraction Modules
import rpc_abstraction
import sql_abstraction
import api_abstraction
import mech_abstraction

# Logging Configuration
logger = logging.getLogger('__Aurtip__')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh_debug = logging.FileHandler('debug.log')
fh_debug.setLevel(logging.DEBUG)
# create file handler which logs only critical messages
fh_crit = logging.FileHandler('critical.log')
fh_crit.setLevel(logging.CRITICAL)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh_crit.setFormatter(formatter)
fh_debug.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh_debug)
logger.addHandler(fh_crit)
logger.addHandler(ch)

# Main Function #
#               #
logger.debug("###### Starting Main Function TIPBOT v1.0 ######")

# define connection settings
DB_PROFILE = "mysql" 
RPC_PROFILE = "auroracoind"
API_ROUTES = {"bland": ["bland"]} 
#API_ROUTES = {"phpbb": ["auroraspjall", "jeppaspjall", "skyttur", "islandrover", "blyfotur", "kruser", "mbclub"]} 
#API_ROUTES = {"test": ["test"]}

# create abstracted objects for db and rpc connections based on settings defined above
db = sql_abstraction.SqlConnection(DB_PROFILE)
rpc = rpc_abstraction.BitcoinRpc(RPC_PROFILE)
bbmech = mech_abstraction.Mechanizer()

# Get and process new exchange rate
exchange = exchangeRate.exchangeRateProcessor(db)

# interate through all routes, get and process payloads
for api_profile, api_sites in API_ROUTES.items():
    for site in api_sites:
        logger.debug("---Starting %s API Profile for %s site---" % (api_profile, site))
        # Create api object for the specific type and site to parse
        try:
            api = api_abstraction.ApiConnection(api_profile, site)
        except Exception as e:
            logger.debug("---API CONNECTION FAIL!!  %s API Profile for %s site---" % (api_profile, site))
            import traceback, os.path
            top = traceback.extract_stack()[-1]
            print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
            print e
            fail = True
        # Build payload from an API source
        forumPayload = payload.Payload(api_profile, api, db)
        try:
            pass
            # Process the payload into command calls and return messages to users
            forumProcessList = payloadProcessor.PayloadProcessor(forumPayload.payload, api, db, rpc, exchange)
        except Exception as e:
            logger.debug("---PAYLOAD PROCESSING FAILED!!  %s API Profile for %s site---" % (api_profile, site))
            print e
            fail = True
        try:
            pass
            # Process messages into forum posts and emails
            forumMessenger = messenger.Messenger(db, bbmech, forumProcessList, api)
        except Exception as e:
            import traceback, os.path
            top = traceback.extract_stack()[-1]
            print ', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
            print e
            logger.debug("---MESSAGE PROCESSING FAILED!!  %s API Profile for %s site---" % (api_profile, site))
            fail = True
logger.debug("---Forum Check Script Completed---")

# Check all user addresses for deposits
bankMessenger = messenger.Messenger(db, bbmech)
bankPayload = bank.BankPayload("test", api, db, rpc, bankMessenger)

logger.debug("---Bank Script Completed---")
