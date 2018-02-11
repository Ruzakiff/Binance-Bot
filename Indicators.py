#imports
from binance.client import Client
import config
import sys
import json
import numpy as np
import time
from initalize import *
import talib
#initializations
lengthTime=172800
ema=[0]
ethbtc_close=np.array([])
#avggain and loss persists from other script, gucci
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
datafile=open("/Users/ryan/Desktop/inodawey/ethbtc_close.txt", "r")
while 1:
    where = datafile.tell()
    line = datafile.readline()
    if not line:
        time.sleep(1)
        datafile.seek(where)
    else:
    	#update every second
    	ethbtc_close.append(float(line[21:31])) #might not be global, might need fix if main cant reference
    	if(len(ethbtc_price)>lengthTime):
    		del ethbtc_price[0]
		sma=talib.SMA(ethbtc_close,timeperiod=lengthTime)
		ema=talib.EMA(ethbtc_close,timeperiod=lengthTime)
		rsi=talib.RSI(ethbtc_close,timeperiod=lengthTime)
		hMacD,mMacD,lMacD=talib.MACD(ethbtc_close)#default intervals
		cci=talib.CCI(ethbtc_high,ethbtc_low,ethbtc_close,timeperiod=lengthTime)
		
		
						#CODE BELOW THIS LINE IS DUMB#
####################################################################################################################################################################################################################################################################################
#indicators assume all needed info is present
#indicators need every second to maintain accuracy
#not worrying about triggers for now
def sma(seconds,check): #check is trigger logic (if check is above certain number buy or something)
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
def rsi():
	currentGains=0
	currentLosses=0
	if((ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2])>0):
       		currentGains=ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2])
         	currentLosses=0
	else if((ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2])<0)):
        	currentGains=0
        	currentLosses=abs(ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2]))
	else:
        	currentGains=0
         	currentLosses=0
	avgGain=(13*avggain + cureentgains)/14 #this is setting avggain and loss that is from intialize. values persist
	avgLoss=(13*avgloss + currentloss)/14
	Rs = avggain/avgloss
	rsi.append(100-(100/1+rs))
	if(len(rsi)>172800):
		del rsi[0]
def boll():
	temp=0
	for x in xrange(0,172800):
		temp=temp+ethbtc_price[x]
	middle.append((temp/172800))
	upper.append((temp/172800)+(np.std(ethbtc_price)*2))
	lower.append((temp/172800)-(np.std(ethbtc_price)*2))
	if(len(middle)>lengthTime):
		del middle[0]
	if(len(upper)>lengthTime):
		del upper[0]
	if(len(lower)>lengthTime):
		del lower[0]
	
