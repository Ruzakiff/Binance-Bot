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
#everything is done in base, unless for binanace api

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

#sma
#day
close200=np.array([])
close150=np.array([])
close100=np.array([])
close50=np.array([])

#bollinger
bollLength=60000
highBoll=np.array([])
midBoll=np.array([])
lowBoll=np.array([])


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
kellyReady=False

accountBalanceBase=0
accountBalanceQuote=0



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
bollShout=np.array([])
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
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global sellPrice
	global amountSellBase
	global amountSellQuote
	global difference
	buyPrice=np.append(buyPrice,quoteBase_close[len(quoteBase_close)-1])
	if(kellyReady):
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*kellyCoeff*maxPercent)
	else:
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*minPercent)
	#quote*price=base
	#fix rounding truncate
	temp=amountBuyBase[len(amountBuyBase)-1]/buyPrice[len(buyPrice)-1]
	amountBuyQuote=np.append(amountBuyBase,math.floor(temp))
	#kellyReady?...urg
	#rounding, truncate
	order = client.order_market_buy(
		symbol=pair,
		quantity=amountBuyQuote[len(amountBuyQuote)-1],
		recvWindow=5000)

	return order

def Sell():
	#truncate amount
	global kellyReady
	global kellyCoeff
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global sellPrice
	global amountSellBase
	global amountSellQuote
	global difference
	kellyReady=False
	sellPrice=np.append(sellPrice,quoteBase_close[len(quoteBase_close)])
	for x in range(0,len(amountBuyQuote)):
		amountSellQuote=np.append(amountSellQuote,amountBuyQuote[x])
		amountSellBase=np.append(amountSellBase,amountSellQuote[x]*sellPrice[len(sellPrice)-1])
		difference=np.append(difference,amountSellBase[x]-amountBuyBase[x])

	while(len(difference)>kellyLength):
		difference=np.delete(difference,0)
	if(len(difference)==kellyLength):
		try:
			gains=0.0
			losses=0.0
			gainCount=0.0
			lossCount=0.0
			for x in range(0,len(difference)):
				if(difference[x]>0):
					gains=gains+difference[x]
					gainCount=gainCount+1
				if(difference[x]<0):
					losses=losses+abs(difference[x])
					lossCount=lossCount+1
			avgGainKelly=gains/gainCount
			avgLossKelly=losses/lossCount
			w=gainCount/len(difference)
			r=avgGainKelly/avgLossKelly
			kellyCoeff=w-((1-w)/r)
			kellyReady=True
		except:
			sendNotification("Stopped","Error\nBot Stopped:Kelly Divide By 0")
			sys.exit("Divide By 0")
	else:
		kellyReady=False
	amountSell=0
	for x in range(0,len(amountSellQuote)):
		amountSell=amountSell+amountSellQuote[x]
	#if we have content to sell (not first sell/buy) then sell logic
	order = client.order_market_sell(
		symbol=pair,
		quantity=amountSell,
		recvWindow=5000)
	#wipe
	amountSellQuote=np.array([])
	amountSellBase=np.array([])
	amountBuyQuote=np.array([])
	amountBuyBase=np.array([])
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
		avgRsi=temp/len(rsiValue)
		if(avgRsi<30):
			rsiShout=np.append(rsiShout,1)
		elif(avgRsi>70):
			rsiShout=np.append(rsiShout,-1)
		else:
			rsiShout=np.append(rsiShout,0)


	#update values
	#if not stoploss
	#check marketdireciton
	#checkShout buy/sell
def atrUpdate():
	#open high low
	#high-low abs
	#high-open abs
	#low-open abs
	#choose biggest range
	#tr=biggest
	#14 periods(minutes)
	#first atr=avg 14 tr's
	#next atr's
	#previous atr*13+currentTR
	#divide 14
	#guccigang

def atrListen():

	return 1

def bollUpdate():
	global lowBoll
	global midBoll
	global highBoll
	if(len(quoteBase_close)==bollLength):
		std=np.std(quoteBase_close)
		avg=talib.SMA(quoteBase_close,timeperiod=len(quoteBase_close))
		avg=avg[len(avg)-1]
		highBoll=np.append(highBoll,avg+(2*std))
		lowBoll=np.append(lowBoll,avg-(2*std))
		midBoll=np.append(midBoll,avg)
def bollListen():
	if(len(lowBoll)>=1 and len(midBoll)>=1 and len(highBoll)>=1):
		if(quoteBase_close[len(quoteBase_close)-1]<lowBoll[len(lowBoll)-1]):
			bollShout=np.append(bollShout,1)
		elif(quoteBase_close[len(quoteBase_close)-1]>highBoll[len(highBoll)-1])
			bollShout=np.append(bollShout,-1)
		else:
			bollShout=np.append(bollShout,0)
	
def marketTypeUpdate():
	global close200
	global close150
	global close100
	global close50
	if(len(close200)==200):
		temp=talib.SMA(close200,199-50,timeperiod=50)
		close50=np.append(close50,temp[len(temp)-1])
		temp=talib.SMA(close200,199-100,timeperiod=100)
		close100=np.append(close100,temp[len(temp)-1])
		temp=talib.SMA(close200,199-150,timeperiod=150)
		close150=np.append(close150,temp[len(temp)-1])

def marketTypeListen():
	global marketTypeShout
	
	if(len(close50)>=1 and len(close100)>=1 and len(close150)>=1):
		if(close150[len(close150)-1]>close50[len(close50)-1]):
			marketTypeShout=np.append(marketTypeShout,-1)
		elif(quoteBase_close[len(quoteBase_close)-1]<close150[len(close150)-1]):
			marketTypeShout=np.append(marketTypeShout,-1)
		elif(quoteBase_close[len(quoteBase_close)-1]<close100[len(close100)-1]):
			if(close100[len(close100)-1]<close100[0]):
				marketTypeShout=np.append(marketTypeShout,-1)
			else:
				marketTypeShout=np.append(marketTypeShout,0)
		elif(quoteBase_close[len(quoteBase_close)-1]<close50[len(close50)-1]):
			if(close100[len(close100)-1]<close100[0]):
				marketTypeShout=np.append(marketTypeShout,0)
			else:
				marketTypeShout=np.append(marketTypeShout,1)
		else:
			marketTypeShout=np.append(marketTypeShout,1)


	
client=login()
tickerData=open(tickerRead+".txt","r")
klineData=open(klineRead+".txt","r")
while 1:
	whereTick=tickerData.tell()
	lineTick=tickerData.readline()
	if not lineTick:
		tickerData.seek(whereTick)
	else:
		quoteBase_close=np.append(quoteBase_close,float(lineTick[31:40]))
		while(len(quoteBase_close)>bollLength):
			quoteBase_close=np.delete(quoteBase_close,0)
	whereKline=klineData.tell()
	lineKline=klineData.readline()
	if not lineKline:
		klineData.seek(whereKline)
	else:
		quoteBase_high=np.append(quoteBase_high,float(lineKline[32:42]))
		quoteBase_low=np.append(quoteBase_low,float(lineKline[46:56]))
		while(len(quoteBase_high)>actionPeriod):
			quoteBase_high=np.delete(quoteBase_high,0)
		while(len(quoteBase_low)>actionPeriod):
			quoteBase_low=np.delete(quoteBase_low,0)

	rsiUpdate()
	atrUpdate()
	bollUpdate()

	marketTypeValue()
	
	#rsiValue=np.append(rsiValue,rsiUpdate())
	#atrValue=np.append(atrValue,atrUpdate())
	#marketTypeValue=np.append(marketTypeValue,marketTypeUpdate())
	while(len(rsiValue)>actionPeriod):
		rsiValue=np.delete(rsiValue,0)
	while(len(atrValue)>actionPeriod):
		atrValue=np.delete(atrValue,0)
	while(len(close150)>actionPeriod):
		close150=np.delete(close150,0)
	while(len(close100)>actionPeriod):
		close100=np.delete(close100,0)
	while(len(close50)>actionPeriod):
		close50=np.delete(close50,0)
	while(len(lowBoll)>actionPeriod):
		lowBoll=np.delete(lowBoll,0)
	while(len(midBoll)>actionPeriod):
		midBoll=np.delete(midBoll,0)
	while(len(highBoll)>actionPeriod):
		highBoll=np.delete(highBoll,0)

	rsiListen()
	atrListen()
	bollListen()

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
				if(bollShout[len(bollShout)-1]==1):
					Buy()
				elif(bollShout[len(bollShout)-1]==-1):
					Sell()
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
				
	
				
