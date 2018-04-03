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

#bot assumptions
#We can buy as much we want
#But we sell everything
#LAST index is latest value

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
actionPeriod=30
lengthTime=1000


maxPercent=0.3
minPercent=0.1
minAmount=1

#rsi
rsiPeriod=14
avgGainRSI=0
avgLossRSI=0

#atr
atrPeriod=14

quoteTransactionAmount=0
#amountQuote

#kelly
kellyLength=60
kellyCoeff=1
amountBuyBase=np.array([])
amountBuyQuote=np.array([])
buyPrice=np.array([])
sellPrice=np.array([])
amountSellBase=np.array([])
amountSellQuote=np.array([])
difference=np.array([])




quoteBase_close=np.array([])
quoteBase_high=np.array([])
quoteBase_low=np.array([])

rsiValue=np.array([])
atrValue=np.array([])
marketTypeValue=np.array([])
#other indicators as well
#include bull/bear
#stoploss

rsiShout=np.array([])
atrShout=np.array([])
marketTypeShout=np.array([])
#other indicators
#for buying selling determine
#bull/bear


#price/portion sizing
#kelly



#defining functions
#rsi
#rsiShout
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
def Buy():
	#truncate floor
	global quoteTransactionAmount
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global sellPrice
	global amountSellBase
	global amountSellQuote
	global difference
	buyPrice=np.append(buyPrice,quoteBase_close[len(quoteBase_close)-1])
	quoteAmount=quoteTransactionAmount*kellyCoeff*maxPercent
	#kellyReady?...urg
	#rounding, truncate
	amountBuyBase=np.append(amountBuyBase,quoteBase_close[len()])
	order = client.order_market_buy(
		symbol=pair,
		quantity=amount,
		recvWindow=5000)

	return order

def Sell():
	#truncate amount
	global quoteTransactionAmount
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global sellPrice
	global amountSellBase
	global amountSellQuote
	global difference
	#if we have content to sell (not first sell/buy) then sell logic
	order = client.order_market_sell(
		symbol=pair,
		quantity=amount,
		recvWindow=5000)
	#kelly logic
	return order
def rsiUpdate():
	global rsiValue
	global avgGainRSI
	global avgLossRSI
	rs=0
	change=0
	currentGains=0
	currentLosses=0
	if(len(quoteBase_close)==rsiPeriod):
		tempGain=0
		tempLoss=0
		for x in range(0, rsiPeriod-2):
		 	change=quoteBase_close[x+1]-quoteBase_close[x]
		 	if(change>0):
		 		tempGain=tempGain+change
		 	elif(change<0):
		 		tempLoss=tempLoss+abs(change)
		avgGainRSI=tempGain/rsiPeriod
		avgLossRSI=tempLoss/rsiPeriod
	 	rs = avgGainRSI/avgLossRSI
		rsiValue=np.append(rsiValue,100-(100/(1+rs)))
	elif(len(quoteBase_close)>rsiPeriod):
		change=quoteBase_close[len(quoteBase_close)-1]-quoteBase_close[len(quoteBase_close)-2]
		if(change>0):
			currentGains=change
			currentLosses=0
		elif(change<0):
			currentGains=0
			currentLosses=abs(change)
		else:
			currentGains=0
			currentLosses=0
		avgGainRSI=((rsiPeriod-1)*avgGainRSI + currentGains)/rsiPeriod #this is setting avggain and loss that is from intialize. values persist
		avgLossRSI=((rsiPeriod-1)*avgLossRSI + currentLosses)/rsiPeriod
		rs = avgGainRSI/avgLossRSI
		rsiValye=np.append(rsiValue,100-(100/(1+rs)))
def rsiListen():
	global rsiShout
	if(len(rsiValue)>=actionPeriod):
		temp=0
		for x in range(0,len(rsiValue)):
			temp=temp+rsiValue[x]
		rsiShout=np.append(rsiShout,temp/len(rsiValue))


	#update values
	#if not stoploss
	#check marketdireciton
	#checkShout buy/sell
def atrUpdate():

def atrListen():

	return 1
	
def marketTypeUpdate():

def marketTypeListen():
	
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
	if not lineKline:
		klineData.seek(whereKline)
	else:
		quoteBase_high=np.append(quoteBase_high,float(lineKline[32:42]))
		quoteBase_low=np.append(quoteBase_low,float(lineKline[46:56]))

	rsiUpdate()
	atrUpdate()
	marketTypeValue()
	#rsiValue=np.append(rsiValue,rsiUpdate())
	#atrValue=np.append(atrValue,atrUpdate())
	#marketTypeValue=np.append(marketTypeValue,marketTypeUpdate())
	while(len(rsiValue)>actionPeriod):
		rsiValue=np.delete(rsiValue,0)
	while(len(atrValue)>actionPeriod):
		atrValue=np.delete(atrValue,0)
	while(len(marketTypeValue)>actionPeriod):
		marketTypeValue=np.delete(marketTypeValue,0)
	rsiListen()
	atrListen()
	marketTypeListen()
	
	#rsiShout=np.append(rsiShout,rsiListen())
#	atrShout=np.append(atrShout,atrListen())
	#marketTypeShout=np.append(marketTypeShout,marketTypeListen())

	
	#stoploss
	if(atrShout[len(atrShout)-1]==-1):
		Sell()
	else:
		#bull=1
		#side=0
		#bear=-1
		if(marketTypeShout[len(marketTypeShout)-1]==1):
			#bulls
			if(len(quoteBase_close)%actionPeriod==0):
				#for each indiactors we care about particular to market
				#based off those, buy, sell or nothing
		elif(marketTypeShout[len(marketTypeShout)-1]==0):
			#side
			if(len(quoteBase_close)%actionPeriod==0):
				if(rsiShout[len(rsiShout)-1]==1):
					Buy()
				elif(rsiShout[len(rsiShout)-1]==-1):
					Sell()
				#for each indiactors we care about particular to market
				#based off those, buy, sell or nothing		
		elif(marketTypeShout[len(marketTypeShout)-1]==-1):
			#bear
			if(len(quoteBase_close)%actionPeriod==0):
				#for each indiactors we care about particular to market
				#based off those, buy, sell or nothing
				
	
				
