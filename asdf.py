from binance.client import Client
import numpy as np
import config
import sys
import time
import talib
import json
import datetime
import os
import smtplib
from decimal import *
import math






avgGainRSI=0
avgLossRSI=0

rsi=np.array([])


#files
klineRead="/Users/ryan/Desktop/Doggo4/klines"
tickerRead="/Users/ryan/Desktop/Doggo4/ticker"
resultFile="/Users/ryan/Desktop/Doggo4/trades"
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']

#currency settings
pair='ADAETH'
base="ETH"
quote="ADA"

#Time seconds
actionPeriod=15
lengthTime=1000


quoteBase_close=np.array([])
quoteBase_high=np.array([])
quoteBase_low=np.array([])

rsiValue=np.array([])
#other indicators as well
#include bull/bear
#stoploss

rsiShout=np.array([])
#other indicators
#for buying selling determine
#bull/bear


#price/portion sizing
#kelly
kellyLength=60
maxPercent=0.3
minPercent=0.1
minAmount=1


#defining functions
#rsi
#rsishout
#kelly
#bullbear value
#bull bear shout
#buy
#sell
#send notificaiton


def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client
def sendNotification(subject,mesg):
	try:
		sent_from = gmail_user   
		msg='Subject:'+subject+'\n\n'+mesg.format(subject)
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(gmail_user, send_list, msg)
		server.close()
		print 'Email sent!'
	except:
		print 'Email Send Failure'
def Buy(amount):
	order = client.order_market_buy(
		symbol=pair,
		quantity=amount,
		recvWindow=5000)
	return order

def Sell(amount):
	order = client.order_market_sell(
		symbol=pair,
		quantity=amount,
		recvWindow=5000)
	return order
def rsiUpdate():
	print "asdf"
def rsiListen():

	#update values
	#if not stoploss
	#check marketdireciton
	#checkShout buy/sell
client=login()
tickerData=open(tickerRead+".txt","r")
klineData=open(klineRead+".txt","r")
while 1:
	whereTick=tickerData.tell()
	lineTick=tickerData.readline()
	if not lineTick:
		tickerData.seek(whereTick)
	else:
		quoteBase_close=np.append(quoteBase_close,float(lineTick[]))
	whereKline=klineData.tell()
	lineKline=klineData.readline()
	if not lineTick:
		klineData.seek(whereKline)
	else:
		quoteBase_high=np.append(quoteBase_high,float(lineKline[32:42]))
		quoteBase_low=np.append(quoteBase_low,float(lineKline[46:56]))






























