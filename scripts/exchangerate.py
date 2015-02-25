#!/usr/bin/env python
# exchangerate.py
# This app gets AUR / BTC exchange rate from Cryptsy.com and puts into abe databse with datetime
#
#
# Author: Joseph Lee
# Date: January 2015
# Email: joseph.lee.esl@gmail.com

url = 'http://pubapi.cryptsy.com/api.php?method=singlemarketdata&marketid=160'

from urllib2 import Request, urlopen, URLError
from pprint import pprint
import json
import psycopg2


#Try to get the page from Cryptsy
request = Request(url)
try:
	response = urlopen(request)
except URLError, e:
    print 'Error code:', e

#Parse the page for most recent AUR price and other data
#pprint (exchangeJSON)

data = json.load(response)

success = data["success"]
lastAURprice = data["return"]["markets"]["AUR"]["lasttradeprice"]
lasttradetime = data["return"]["markets"]["AUR"]["lasttradetime"]

print "Last AUR Price: " + lastAURprice
print "Last Trade Datetime: " + lasttradetime

cur.execute("INSERT INTO exchange_rate (firstcurrency, secondcurrency, rate, datetime) VALUES (%s, %s, %s, %s )", ("AUR", "BTC", lastAURprice, lasttradetime))

print "Entered exchange rate data into database"

