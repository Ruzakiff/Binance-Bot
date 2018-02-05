#imports
from binance.client import Client
import config
import sys
import json
import numpy as np
import time
from indicators import *
import matplotlib.pyplot as plt
#initializations
lengthTime=172800
ema=[0]
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
datafile=open("/Users/ryan/Desktop/inodawey/data.txt", "r")
while 1:
    where = datafile.tell()
    line = datafile.readline()
    if not line:
        time.sleep(1)
        datafile.seek(where)
    else:
    	#update every second
    	ethbtc_price.append(float(line[21:31]))
    	if(len(ethbtc_price)>lengthTime):
    		del ethbtc_price[0]

#indicators need every second to maintain accuracy
#not worrying about triggers for now
def sma(seconds,check):
	temp=0
	for x in xrange(0,seconds):
		temp=temp+ethbtc_price[x]
	sma.append((temp/seconds))
	if(len(sma)>lengthTime):
		del sma[0]
	#write true false logic, the d
	#if(sma[123]>check):
		#return True
def ema():
	ema.append((ethbtc_price-ema[len(ema-1)])*.181818)+len(ema-1)
	if(len(ema)>lengthTime):
		del ema[0]
