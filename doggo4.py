from binance.client import Client
import talib
import numpy as np
import time
from indicators import *
buyAmount=0
sellAmount=0
def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client

#main
client=login();
while 1:
	if(rsi[len(rsi)-1]<=30):
  order = client.order_market_buy(
      symbol='ETHBTC',
      quantity=buyAmount)
    
    
