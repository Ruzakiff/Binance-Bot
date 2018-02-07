#TODO
#Continuiously get all data that is needed for bot to start
#(rsi,sma for middle boll, etc)
#feed data to indicators
#Do not let bot start until all data is retreived, and keep updating until bot starts, all arrays must be filled
#Give data to bot
#should i write to different files for each one? (rsi, boll,etc) or same file
from binance.client import Client
import config
import sys
import json
import numpy as np
import time
from indicators import *
import matplotlib.pyplot as plt

def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client
def canStart():
	return False

#main
client=login();
#Continuiously get all data that is needed for bot to start
#(rsi,sma for middle boll, etc)
#feed data to indicators
#Do not let bot start until all data is retreived, and keep updating until bot starts, all arrays must be filled
#Give data to bot
