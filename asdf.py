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
import re
import schedule
from coinmarketcap import Market
#bot assumptions
#shout arrays are filled every second with some sort of data
#whether its -1,0,or 1
#We can buy as much we want
#But we sell everything
#LAST index is latest value
#everything is done in base, unless for binanace api

#files
quoteHist="/Users/ryan/Desktop/Doggo4/ADA Hist"
baseHist="/Users/ryan/Desktop/Doggo4/ETH Hist"
klineRead="/Users/ryan/Desktop/Doggo4/klines"
tickerRead="/Users/ryan/Desktop/Doggo4/ticker"
resultFile="/Users/ryan/Desktop/Doggo4/trades"
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']

#currency settings
pair='ADAETH'
base="ETH"
quote="ADA"
baseFull="Ethereum"
quoteFull="Cardano"
precision=1 #1=0 decimals
#Time seconds
actionPeriod=15
lengthTime=1209600 #14 day seconds




#sma
#day
histQuoteClose=np.array([])
histBaseClose=np.array([])
close200=np.array([])
close150=np.array([])
close100=np.array([])
close50=np.array([])


#bollinger
bollLength=60000 #cannot be greater than lengthtime!
highBoll=np.array([])
midBoll=np.array([])
lowBoll=np.array([])
bollShout=np.array([])


#rsi
rsiPeriod=14
rsiValue=np.array([])
rsiShout=np.array([])
avgGainRSI=0
avgLossRSI=0

#atr
atrPeriod=14
atrValue=np.array([])
atrShout=np.array([])
lowerStop=0

macdValue=np.array([])
macdSignal=np.array([])
macdHisto=np.array([])
macdShout=np.array([])
macdFastLength=604800 #7day seconds
macdSlowLength=lengthTime
macdSignalLength=777600 #9day seconds

quoteTransactionAmount=0
#amountQuote

#kelly
kellyLength=60
kellyCoeff=1
maxPercent=0.3
minPercent=0.1
minAmount=1
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
quoteBase_open=np.array([])
quoteBase_high=np.array([])
quoteBase_low=np.array([])

marketTypeValue=np.array([])
marketTypeShout=np.array([])




#other indicators
#for buying selling determine
#bull/bear


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
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global amountSellBase
	global amountSellQuote
	global difference
	global accountBalanceBase
	global accountBalanceQuote
	accountStringQuote=json.dumps(client.get_asset_balance(quote))
	accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
	accountStringBase=json.dumps(client.get_asset_balance(base))
	accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
	buyPrice=np.append(buyPrice,quoteBase_close[len(quoteBase_close)-1])
	if(kellyReady):
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*kellyCoeff*maxPercent)
	else:
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*minPercent)
	#quote*price=base
	#fix rounding truncate
	temp=amountBuyBase[len(amountBuyBase)-1]/buyPrice[len(buyPrice)-1]
	temp=temp*precision
	temp=double(math.floor(temp))/double(precision)
	amountBuyQuote=np.append(amountBuyBase,temp)
	order = client.order_market_buy(
		symbol=pair,
		quantity=amountBuyQuote[len(amountBuyQuote)-1],
		recvWindow=5000)
	accountStringQuote=json.dumps(client.get_asset_balance(quote))
	accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
	accountStringBase=json.dumps(client.get_asset_balance(base))
	accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
	return order

def Sell():
	global kellyReady
	global kellyCoeff
	global amountBuyBase
	global amountBuyQuote
	global sellPrice
	global amountSellBase
	global amountSellQuote
	global difference
	global accountStringBase
	global accountStringQuote
	accountStringQuote=json.dumps(client.get_asset_balance(quote))
	accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
	accountStringBase=json.dumps(client.get_asset_balance(base))
	accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
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
	amountSell=amountSell*precision
	amountSell=double(math.floor(amountSell))/double(precision)
	order = client.order_market_sell(
		symbol=pair,
		quantity=amountSell,
		recvWindow=5000)
	accountStringQuote=json.dumps(client.get_asset_balance(quote))
	accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
	accountStringBase=json.dumps(client.get_asset_balance(base))
	accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
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
	if(len(quoteBase_close)==rsiPeriod+1):
		tempGain=0
		tempLoss=0
		for x in range(0, rsiPeriod):
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
		rsiValue=np.append(rsiValue,100-(100/(1+rs)))
	if(len(rsiValue)>1):
		print rsiValue[len(rsiValue)-1]
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
def atrUpdate():
	global atrValue
	tr=0
	if(len(quoteBase_open)==atrPeriod and len(quoteBase_high)==atrPeriod and len(quoteBase_low)==atrPeriod):
		temp=0
		tr=0
		for x in range(0,atrPeriod):
			tr=0
			if(quoteBase_high[x]-quoteBase_low[x]>tr):
				tr=quoteBase_high[x]-quoteBase_low[x]
			if(math.fabs(quoteBase_high[x]-quoteBase_open[x])>tr):
				tr=math.fabs(quoteBase_high[x]-quoteBase_open[x])
			if(math.fabs(quoteBase_low[x]-quoteBase_open[x])>tr):
				tr=math.fabs(quoteBase_low[x]-quoteBase_open[x])
			temp=temp+tr
		atrValue=np.append(atrValue,temp/atrPeriod)
	elif(len(quoteBase_open)>atrPeriod and len(quoteBase_high)>atrPeriod and len(quoteBase_low)>atrPeriod):
		tr=0
		#latest value right?...
		if(quoteBase_high[len(quoteBase_high)-1]-quoteBase_low[len(quoteBase_low)-1]>tr):
			tr=quoteBase_high[len(quoteBase_high)-1]-quoteBase_low[len(quoteBase_low)-1]
		if(math.fabs(quoteBase_high[len(quoteBase_high)-1]-quoteBase_open[len(quoteBase_open)-1])>tr):
			tr=math.fabs(quoteBase_high[len(quoteBase_high)-1]-quoteBase_open[len(quoteBase_open)-1])
		if(math.fabs(quoteBase_low[len(quoteBase_low)-1]-quoteBase_open[len(quoteBase_open)-1])>tr):
			tr=math.fabs(quoteBase_low[len(quoteBase_low)-1]-quoteBase_open[len(quoteBase_open)-1])
		temp=((atrValue[len(atrValue)-1]*(atrPeriod-1))+tr)/atrPeriod #double?
		atrValue=np.append(atrValue,temp)

	if(len(atrValue)>0 and len(buyPrice)>0):
		if(quoteBase_close[len(quoteBase_close)-1]>buyPrice[len(buyPrice)-1]):
			lowerStop=quoteBase_close[len(quoteBase_close)-1]
		else:
			lowerStop=buyPrice[len(buyPrice)-1]-(2*atrValue[len(atrValue)-1])
				    	
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
	global atrShout
	global lowerStop
	if(len(atrValue)>0 and len(buyPrice)>0):
		if(quoteBase_close[len(quoteBase_close)-1]<=lowerStop):
			atrShout=np.append(atrShout,-1)
		else:
			atrShout=np.append(atrShout,0)

def bollUpdate():
	global lowBoll
	global midBoll
	global highBoll
	#>= bolllength?...
	if(len(quoteBase_close)>=bollLength):
		std=np.std(quoteBase_close)
		tempArray=np.array([])
		tempArray=quoteBase_close[len(quoteBase_close)-bollLength:len(quoteBase_close)]
		avg=talib.SMA(tempArray,timeperiod=bollLength)
		avg=avg[len(avg)-1]
		highBoll=np.append(highBoll,avg+(2*std))
		lowBoll=np.append(lowBoll,avg-(2*std))
		midBoll=np.append(midBoll,avg)
def bollListen():
	if(len(lowBoll)>=1 and len(midBoll)>=1 and len(highBoll)>=1):
		if(quoteBase_close[len(quoteBase_close)-1]<lowBoll[len(lowBoll)-1]):
			bollShout=np.append(bollShout,1)
		elif(quoteBase_close[len(quoteBase_close)-1]>highBoll[len(highBoll)-1]):
			bollShout=np.append(bollShout,-1)
		else:
			bollShout=np.append(bollShout,0)

def macdUpdate():
	global macdValue,macdShout,macdSignal,macdHisto
	tempArray=np.array([])
	tempFast=np.array([])
	tempSignal=np.array([])
	tempSlow=np.array([])
	if(len(quoteBase_close)>=lengthTime):
		tempArray=quoteBase_close[len(quoteBase_close)-macdFastLength:len(quoteBase_close)]
		tempFast=talib.EMA(tempArray,timeperiod=macdFastLength)

		tempArray=quoteBase_close[len(quoteBase_close)-macdSignalLength:len(quoteBase_close)]
		tempSignal=talib.EMA(tempArray,timeperiod=macdSignalLength)

		tempArray=quoteBase_close[len(quoteBase_close)-macdSlowLength:len(quoteBase_close)]
		tempSlow=talib.EMA(tempArray,timeperiod=macdSlowLength)

		emaFast=tempFast[len(tempFast)-1]
		emaSignal=tempSignal[len(tempSignal)-1]
		emaSlow=tempSlow[len(tempSlow)-1]

		macdValue=np.append(macdValue,emaFast-emaSlow)
		macdSignal=np.append(macdSignal,emaSignal)
		macdHisto=np.append(macdHisto,macdValue[len(macdValue)-1]-macdSignal[len(macdSignal)-1])


def macdListen():
	global macdShout
	if(len(macdValue)>=2):
		if(macdHisto[len(macdHisto)-2]>macdValue[len(macdValue)-2]):
			if(macdHisto[len(macdHisto)-1]<=macdValue[len(macdValue)-1]):
				macdShout=np.append(macdShout,-1)
		elif(macdHisto[len(macdHisto)-2]<macdValue[len(macdValue)-2]):
			if(macdHisto[len(macdHisto)-1]>=macdValue[len(macdValue)-1]):
				macdShout=np.append(macdShout,1)
		else:
			macdShout=np.append(macdShout,0)
	
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

def daysma():
	global histQuoteClose
	global histBaseClose
	global close200
	coinRaw=json.dumps(coinmarketcap.ticker(quoteFull))
	histQuoteClose=np.append(histQuoteClose,float(coinRaw[50:58]))
	coinRaw=json.dumps(coinmarketcap.ticker(baseFull))
	histBaseClose=np.append(histBaseClose,float(coinRaw[50:58]))
	close200=np.append(close200,histQuoteClose[len(histQuoteClose)-1]/histBaseClose[len(histBaseClose)-1])


#regex all the other stuff as well? not be lazy
re1='.*?'	# Non-greedy match on filler
re2='[+-]?\\d*\\.\\d+(?![-+0-9\\.])'	# Uninteresting: float
re3='.*?'	# Non-greedy match on filler
re4='[+-]?\\d*\\.\\d+(?![-+0-9\\.])'	# Uninteresting: float
re5='.*?'	# Non-greedy match on filler
re6='[+-]?\\d*\\.\\d+(?![-+0-9\\.])'	# Uninteresting: float
re7='.*?'	# Non-greedy match on filler
re8='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1
rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8,re.IGNORECASE|re.DOTALL)
with open(quoteHist+".txt","r") as out:
	temptxt=out.readlines()
#txt='Jan 05, 2018 1.17 1.25 0.903503 0.999559 508,100,00 030,364,400,000'
for txt in temptxt:
	m = rg.search(txt)
	if m:
		float1=m.group(1)
		histQuoteClose=np.append(histQuoteClose,float1)
with open(baseHist+".txt","r") as out:
	temptxt=out.readlines()
for txt in temptxt:
	m = rg.search(txt)
	if m:
		float1=m.group(1)
		histBaseClose=np.append(histBaseClose,float1)


client=login()
tickerData=open(tickerRead+".txt","r")
klineData=open(klineRead+".txt","r")
coinmarketcap = Market()
for x in range(0,len(histQuoteClose)):
	close200=np.append(close200,float(histQuoteClose[x])/float(histBaseClose[x]))
schedule.every().day.at("11:30").do(daysma)

accountStringQuote=json.dumps(client.get_asset_balance(quote))
accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
accountStringBase=json.dumps(client.get_asset_balance(base))
accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
while 1:
	schedule.run_pending()
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
		quoteBase_open=np.append(quoteBase_open,float(lineKline[18:28]))
		while(len(quoteBase_high)>actionPeriod):
			quoteBase_high=np.delete(quoteBase_high,0)
		while(len(quoteBase_low)>actionPeriod):
			quoteBase_low=np.delete(quoteBase_low,0)
		while(len(quoteBase_open)>actionPeriod):
			quoteBase_open=np.delete(quoteBase_open,0)

		rsiUpdate()
		atrUpdate()
		bollUpdate()
		macdUpdate()
		marketTypeUpdate()
	
		#rsiValue=np.append(rsiValue,rsiUpdate())
		#atrValue=np.append(atrValue,atrUpdate())
		#marketTypeValue=np.append(marketTypeValue,marketTypeUpdate())
		while(len(macdValue)>lengthTime):
			macdValue=np.delete(macdValue,0)
		while(len(macdShout)>lengthTime):
			macdShout=np.delete(macdShout,0)
		while(len(macdSignal)>lengthTime):
			macdSignal=np.delete(macdSignal,0)
		while(len(macdHisto)>lengthTime):
			macdHisto=np.delete(macdHisto,0)
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
		macdListen()
		marketTypeListen()

	
	#rsiShout=np.append(rsiShout,rsiListen())
#	atrShout=np.append(atrShout,atrListen())
	#marketTypeShout=np.append(marketTypeShout,marketTypeListen())

	
	#stoploss
	if(len(atrShout)>0 and len(rsiShout)>0 and len(macdShout)>0 and len(bollShout)>0):
		if(atrShout[len(atrShout)-1]==-1):
			print "Sell ATR"
			#Sell()
		else:
			#bull=1
			#side=0
			#bear=-1
			if(marketTypeShout[len(marketTypeShout)-1]==1):
				#bulls
				if(len(quoteBase_close)%actionPeriod==0):
					if(bollShout[len(bollShout)-1]==1):
						print "Buy Boll"
						#Buy()
					elif(bollShout[len(bollShout)-1]==-1):
						print"Sell Boll"
						#Sell()
			elif(marketTypeShout[len(marketTypeShout)-1]==0):
				#side
				if(len(quoteBase_close)%actionPeriod==0):
					if(rsiShout[len(rsiShout)-1]==1):
						print "Buy RSI"
						#Buy()
					elif(rsiShout[len(rsiShout)-1]==-1):
						print "Sell RSI"
						#Sell()
					#for each indiactors we care about particular to market
					#based off those, buy, sell or nothing		
			elif(marketTypeShout[len(marketTypeShout)-1]==-1):
				#bear
				print "bear"
				if(len(quoteBase_close)%actionPeriod==0):
					if(macdShout[len(macdShout)-1]==1 and rsiShout[len(rsiShout)-1]==1):
						print "Buy macd"
						#Buy()
					elif(macdShout[len(macdShout)-1]==-1 and rsiShout[len(rsiShout)-1]==-1):
						print "Sell macd"
						#Sell()

					#for each indiactors we care about particular to market
					#based off those, buy, sell or nothing
					
		
					
