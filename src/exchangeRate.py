#!/usr/bin/env python
# exchangerate.py
# This app gets AUR / BTC exchange rate from Cryptsy.com and puts into abe databse with datetime
#
#
# Author: Joseph Lee
# Date: January 2015
# Email: joseph.lee.esl@gmail.com

from urllib2 import Request, urlopen, URLError
import requests
import json
import logging

class exchangeRateProcessor:
    def __init__(self, db):
        self.log = logging.getLogger('__Aurtip__')
        self.log.debug("---Exchange Rate Processor Started---")
        aur_btc_url = 'http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=160'
        usd_btc_url = 'http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=2'
        
        response = requests.get(aur_btc_url)
        if response.status_code == 200:
            data = json.loads(response.content)
            success = data["success"]
            lastprice = data["return"]["markets"]["AUR"]["lasttradeprice"]
            lastdatetime = data["return"]["markets"]["AUR"]["lasttradetime"]
            self.log.debug ("Last AUR/BTC Price: %s", lastprice)
            self.log.debug ("Last AUR/BTC Trade Datetime: %s", lastdatetime)
            db.store_exchange_rate("AUR", "BTC", lastprice, lastdatetime)
            self.log.debug ("Entered exchange rate data into database")
        
        response = requests.get(usd_btc_url)
        if response.status_code == 200:
            data = json.loads(response.content)
            success = data["success"]
            lastprice = data["return"]["markets"]["BTC"]["lasttradeprice"]
            lastdatetime = data["return"]["markets"]["BTC"]["lasttradetime"]
            self.log.debug ("Last BTC/USD Price: %s", lastprice)
            self.log.debug ("Last BTC/USD Trade Datetime: %s", lastdatetime)
            db.store_exchange_rate("BTC", "USD", lastprice, lastdatetime)
            self.log.debug ("Entered exchange rate data into database")
            # get AUR to USD exchange rate into object variable
            self.USD_rate = db.get_last_exchange_rate()
            self.log.debug("AUR/USD Exchange rate : %s", self.USD_rate)