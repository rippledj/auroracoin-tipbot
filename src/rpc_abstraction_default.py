# Copyright Licencing:
# MIT Licence

# Project Title: AuroraCoin tip-bot
# Module Title: RPC Abstraction Module
# Author: Joseph Lee
# Email: joseph.lee.esl@gmail.com
# Date: 2015-01-26

# Description:
# This package abstracts the web API connection details.  Profiles for connecting to sources can be created here. 
# The profile name is passed into the object upon creation. 

# Import Basic Modules

import bitcoinrpc.authproxy

class BitcoinRpc:
    def __init__(self, profile):
        # bland.is profile
        if profile == "auroracoind":
	    # Your bitcoind RPC authentication user and password.  Found in the hidded directory of your altcoin.
            BITCOINRPC = 'http://bitcoind_username:bitcoind_RPCpassword_hash:bitcoind_RPC_port/'
            self.bitcoin = bitcoinrpc.authproxy.AuthServiceProxy(BITCOINRPC)
