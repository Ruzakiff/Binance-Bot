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
import imaplib
import email
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
#We do not start bot at 11:30?...
#Do NOT start with quote in account (throws off percent change)
#More ticker points than kline points by atleast +1
#Update all indiactors, regardless if its updated on kline vs ticker
#just repeat old values
#KEEP IN MIND FOR a indicator which retains old values to calculate
#EX RSI

#files
quoteHist="/Users/ryan/Desktop/Doggo4/ADA Hist"
baseHist="/Users/ryan/Desktop/Doggo4/ETH Hist"
klineRead="/Users/ryan/Desktop/Doggo4/klines"
tickerRead="/Users/ryan/Desktop/Doggo4/ticker"
resultFile="/Users/ryan/Desktop/Doggo4/trades"

checkInterval=0.1 #min
checkTime=0
gmail_user = 'doggo4notification@gmail.com'  
gmail_password = 'doggo4notify'
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']

#currency settings
pair='ADAETH'
base="ETH"
quote="ADA"
baseFull="Ethereum"
quoteFull="Cardano"
precision=1 #1=0 decimals,10=1 decimal
#Time seconds
actionPeriod=15
lengthTime=1209600 #14 day seconds
readTick=False
readKline=False
reading=False

stopPercent=0.1
maxPercent=0.3
minPercent=0.1
minAmount=0.003 #in base (ether)

timeCancel=1
tradeID=np.array([])
tradeTime=0
statusChecked=False


#sma
#day
histQuoteClose=np.array([])
histBaseClose=np.array([])
sma200=np.array([])
sma100=np.array([])
sma50=np.array([])
close200=np.array([])


#bollinger
bollLength=300000
#bollLength=300000 #cannot be greater than lengthTime!
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
totalOld=0

quoteBase_close=np.array([])
quoteBase_open=np.array([])
quoteBase_high=np.array([])
quoteBase_low=np.array([])

marketTypeValue=np.array([])
marketTypeShout=np.array([])

run=True

numberbuy=0



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

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login(gmail_user, gmail_password)
def extract_body(payload):
	if isinstance(payload,str):
		return payload
	else:
		return '\n'.join([extract_body(part.get_payload()) for part in payload])
def checkMessage():
	global run
	try:
		conn.select()
		typ, data = conn.search(None, 'UNSEEN')
		for num in data[0].split():
			typ, msg_data = conn.fetch(num, '(RFC822)')
			for response_part in msg_data:
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1])
					subject=msg['subject']                   
					#print(subject)
					payload=msg.get_payload()
					body=extract_body(payload)
					print(body)
					msg="Error\nBot Stopped:"+msg['From']+"\n Turned off Bot!"
					if re.search("STOP",body):
						run=False
						sendNotification("Stopped",msg)
			typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
	except:
		sendNotification("Error","Read Check Failed, Bot Not Stopped!")
		#sendNotification("Stopped","Error\nBot Stopped:Read Check Failed")
		#sys.exit("Read Check Failed")

def Buy():
	global amountBuyBase
	global amountBuyQuote
	global buyPrice
	global amountSellBase
	global amountSellQuote
	global difference
	global accountBalanceBase
	global accountBalanceQuote
	buyPrice=np.append(buyPrice,quoteBase_close[len(quoteBase_close)-1])
	if(kellyReady):
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*kellyCoeff*maxPercent)
	else:
		amountBuyBase=np.append(amountBuyQuote,accountBalanceBase*minPercent)
	#quote*price=base
	#fix rounding truncate
	temp=amountBuyBase[len(amountBuyBase)-1]/buyPrice[len(buyPrice)-1]
	temp=temp*precision
	temp=float(math.floor(temp))/float(precision)
	amountBuyQuote=np.append(amountBuyQuote,temp) #originally np.append(buybase, temp) for some reason
	print "Amount Bought (Quote):",amountBuyQuote[len(amountBuyQuote)-1]
	print "Amount Bought (Base):",amountBuyQuote[len(amountBuyQuote)-1]*buyPrice[len(buyPrice)-1]
	accountBalanceQuote=accountBalanceQuote+amountBuyQuote
	accountBalanceBase=accountBalanceBase-(amountBuyQuote*quoteBase_close[len(quoteBase_close)-1])


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
	global accountBalanceBase #MAKE SURE THIS IN ACTUAL PROGRAM!!!
	global accountBalanceQuote
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
			#sys.exit("Divide By 0")
	else:
		kellyReady=False
	amountSell=0
	for x in range(0,len(amountSellQuote)):
		amountSell=amountSell+amountSellQuote[x]
	#if we have content to sell (not first sell/buy) then sell logic
	amountSell=amountSell*precision
	amountSell=float(math.floor(amountSell))/float(precision)

	print "Amount Sold (Quote):",amountSell
	print "Amount Sold (Base):",amountSell*sellPrice[len(sellPrice)-1]
	accountBalanceQuote=accountBalanceQuote-amountSell
	accountBalanceBase=accountBalanceBase+(amountSell*quoteBase_close[len(quoteBase_close)-1])

	#wipe
	amountSellQuote=np.array([])
	amountSellBase=np.array([])
	amountBuyQuote=np.array([])
	amountBuyBase=np.array([])
def sma(start,end):
	temp=0
	for x in range(start,end):
		temp=temp+quoteBase_close[x]
	return temp/(end-start)


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
		if(avgLossRSI==0):
			rs=0
			rsiValue=np.append(rsiValue,50)
		else:
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
		if(avgLossRSI==0):
			rs=0
			rsiValue=np.append(rsiValue,50)
		else:
	 		rs = avgGainRSI/avgLossRSI
			rsiValue=np.append(rsiValue,100-(100/(1+rs)))
	#if(len(rsiValue)>1):
		#print rsiValue[len(rsiValue)-1]
def rsiListen(market):
	global rsiShout
	low=30
	high=70
	if(market==0):
		low=30
		high=70
	if(market==-1):
		low=40
		high=60
	if(len(rsiValue)>=actionPeriod):
		temp=0
		for x in range(0,len(rsiValue)):
			temp=temp+rsiValue[x]
		avgRsi=temp/len(rsiValue)
		if(avgRsi<low):
			rsiShout=np.append(rsiShout,1)
		elif(avgRsi>high):
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
	#	highBoll,midBoll,lowBoll=talib.BBANDS(quoteBase_close,timeperiod=bollLength)
		std=np.std(quoteBase_close)
	#	tempArray=np.array([])
		#tempArray=quoteBase_close[len(quoteBase_close)-bollLength:len(quoteBase_close)]
		avg=sma(len(quoteBase_close)-bollLength,len(quoteBase_close))
		#avg=talib.SMA(tempArray,timeperiod=bollLength)
		#avg=avg[len(avg)-1]
		highBoll=np.append(highBoll,avg+(0.5*std))
		lowBoll=np.append(lowBoll,avg-(0.5*std))
		midBoll=np.append(midBoll,avg)
def bollListen():
	global bollShout
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
	global sma200
	global sma100
	global sma50
	if(len(close200)>=200 and len(quoteBase_close)>=200):
		sma50=np.append(sma50,sma(len(close200)-50,len(close200)))
		sma100=np.append(sma100,sma(len(close200)-100,len(close200)))
		sma200=np.append(sma200,sma(len(close200)-200,len(close200)))


def marketTypeListen():
	#sma100 first index? always 0?
	global marketTypeShout
	if(len(sma50)>=1 and len(sma100)>=1 and len(sma200)>=1):
	 	if(sma200[len(sma200)-1]>sma50[len(sma50)-1]):
	 		marketTypeShout=np.append(marketTypeShout,-1)
	 	elif(quoteBase_close[len(quoteBase_close)-1]<sma200[len(sma200)-1]):
	 		marketTypeShout=np.append(marketTypeShout,-1)
	 	elif(quoteBase_close[len(quoteBase_close)-1]<sma100[len(sma100)-1]):
	 		if(sma100[len(sma100)-1]<sma100[0]):
	 			marketTypeShout=np.append(marketTypeShout,-1)
	 		else:
	 			marketTypeShout=np.append(marketTypeShout,0)
	 	elif(quoteBase_close[len(quoteBase_close)-1]<sma50[len(sma50)-1]):
	 		if(sma100[len(sma100)-1]<sma100[0]):
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
	re1='.*?'	# Non-greedy match on filler
	re2='[+-]?\\d*\\.\\d+(?![-+0-9\\.])'	# Uninteresting: float
	re3='.*?'	# Non-greedy match on filler
	re4='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'	# Float 1

	rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
	m = rg.search(coinRaw)
	float1=m.group(1)
	histQuoteClose=np.append(histQuoteClose,float1)
		#print "("+float1+")"+"\n"
	#histQuoteClose=np.append(histQuoteClose,float(coinRaw[50:58]))
	coinRaw=json.dumps(coinmarketcap.ticker(baseFull))
	m=rg.search(coinRaw)
	float1=m.group(1)
	histBaseClose=np.append(histBaseClose,float1)
	close200=np.append(close200,histQuoteClose[len(histQuoteClose)-1]/histBaseClose[len(histBaseClose)-1])

def percentChange():
	global totalOld
	totalNew=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
	change=(totalnew-totalOld)/totalOld
	change=change*100
	msg="\nCurrent Account Total (Base):"+str(totalNew)+ \
	"\nYesterdays Account Total (Base):"+str(totalOld)+ \
	"\nPercent Change:"+str(change)
	totalOld=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
	sendNotification("Daily Percent Change",msg)

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

coinmarketcap = Market()
client=login()

f = open(tickerRead+".txt", 'r')
templen=f.readlines()
initialTick=len(templen)
f = open(klineRead+".txt", 'r')
templen=f.readlines()
initialKline=len(templen)



tickerData=open(tickerRead+".txt","r")
klineData=open(klineRead+".txt","r")
tradefile=open(resultFile+".txt","a")

for x in range(0,len(histQuoteClose)):
	close200=np.append(close200,float(histQuoteClose[x])/float(histBaseClose[x]))

schedule.every().day.at("11:30").do(daysma)
schedule.every().day.at("11:30").do(percentChange)

accountStringQuote=json.dumps(client.get_asset_balance(quote))
accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
accountStringBase=json.dumps(client.get_asset_balance(base))
accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])

totalOld=accountBalanceBase



#sendNotification("Started","Bot Started:May The Odds Be Ever In Your Favor\nSend 'STOP' at any time to Stop")

print "Bot Started"
print "Initial Ticker Length:",initialTick
print "Initial Kline Length:",initialKline
print "Account Base:",accountBalanceBase
print "Account Quote:",accountBalanceQuote
while run:
	whereKline=klineData.tell()
	lineKline=klineData.readline()
	reading=False
	if not lineKline:
		reading=False
		klineData.seek(whereKline)
	else:
		reading=True
		quoteBase_high=np.append(quoteBase_high,float(lineKline[32:42]))
		quoteBase_low=np.append(quoteBase_low,float(lineKline[46:56]))
		quoteBase_open=np.append(quoteBase_open,float(lineKline[18:28]))
		while(len(quoteBase_high)>lengthTime):
			quoteBase_high=np.delete(quoteBase_high,0)
		while(len(quoteBase_low)>lengthTime):
			quoteBase_low=np.delete(quoteBase_low,0)
		while(len(quoteBase_open)>lengthTime):
			quoteBase_open=np.delete(quoteBase_open,0)

	whereTick=tickerData.tell()
	lineTick=tickerData.readline()
	if not lineTick:
	 	reading=False
	 	tickerData.seek(whereTick)
	else:
		reading=True
	 	quoteBase_close=np.append(quoteBase_close,float(lineTick[31:40]))
	 	while(len(quoteBase_close)>lengthTime):
	 		quoteBase_close=np.delete(quoteBase_close,0)



	if(reading):
		marketTypeUpdate()
		atrUpdate()
		bollUpdate()
		macdUpdate()
		rsiUpdate()
	
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

		while(len(sma200)>actionPeriod):
			sma200=np.delete(sma200,0)
		while(len(sma100)>actionPeriod):
			sma100=np.delete(sma100,0)
		while(len(sma50)>actionPeriod):
			sma50=np.delete(sma50,0)
		while(len(lowBoll)>actionPeriod):
			lowBoll=np.delete(lowBoll,0)
		while(len(midBoll)>actionPeriod):
			midBoll=np.delete(midBoll,0)
		while(len(highBoll)>actionPeriod):
			highBoll=np.delete(highBoll,0)

		marketTypeListen()
		atrListen()
		bollListen()
		macdListen()
		if(len(marketTypeShout)>0):
			rsiListen(marketTypeShout[len(marketTypeShout)-1])

		print "Info Updated:",datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")

		if(True):
			#checkMessage()
			if(len(atrShout)>0):
				if(atrShout[len(atrShout)-1]==-1):
					print "Sell Stop"
					Sell()
					print "ATR:"+str(atrValue[len(atrValue)-1])
					print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
					print "Buy Price:"+str(buyPrice[len(buyPrice)-1])
					print "Lower Limit:"+str(lowerStop)
					#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
					#accountBalanceQuote=0
					totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
					print "Account Balance (Quote):"+str(accountBalanceQuote)
					print "Account Balance (Base):"+str(accountBalanceBase)
					print "Account Balance Total (Base):"+str(totalAccount)
			else:
				print "ATR Not Ready"
			if(len(marketTypeShout)>0):
					#bull=1
				if(marketTypeShout[len(marketTypeShout)-1]==1):
					#bulls
					if(len(quoteBase_close)%actionPeriod==0):
						if(len(bollShout)>0):
							print "Bull Market"
							print "Low Boll:",str(lowBoll[len(lowBoll)-1])
							print "Mid Boll:",str(midBoll[len(midBoll)-1])
							print "High Boll:",str(highBoll[len(highBoll)-1])
							print "Price:",str(quoteBase_close[len(quoteBase_close)-1])
							print "Account Balance (Quote):",str(accountBalanceQuote)
							print "Account Balance (Base):",str(accountBalanceBase)
							print "Account Balance Total (Base):",str(accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1]))
							
							if(bollShout[len(bollShout)-1]==1):
								print "Buy Bull"
								Buy()
								print "Bull Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceQuote=accountBalanceQuote+quoteTransactionAmount
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)

							elif(bollShout[len(bollShout)-1]==-1 and amountBuyQuote>0):
								print"Sell Bull"
								Sell()
								print "Bull Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								#accountBalanceQuote=0
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)
						else:
							print "Boll Not Ready"
				elif(marketTypeShout[len(marketTypeShout)-1]==0):
					#side
					if(len(quoteBase_close)%actionPeriod==0):
						if(len(rsiShout)>0):
							print "Side Market"
							print "RSI:",rsiValue[len(rsiValue)-1]
							print "Price:",str(quoteBase_close[len(quoteBase_close)-1])
							print "Account Balance (Quote):",str(accountBalanceQuote)
							print "Account Balance (Base):",str(accountBalanceBase)
							print "Account Balance Total (Base):",str(accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1]))
							if(rsiShout[len(rsiShout)-1]==1):
								print "Buy Side"
								Buy()
								print "Side Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceQuote=accountBalanceQuote+quoteTransactionAmount
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)
								#sendNotification("Buying",msg)
							elif(rsiShout[len(rsiShout)-1]==-1 and amountBuyQuote>0):
								print "Sell Side"
								Sell()
								print "Bull Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
							#	accountBalanceQuote=0
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)
						else:
							print "RSI Not Ready"
						#for each indiactors we care about particular to market
						#based off those, buy, sell or nothing		
				elif(marketTypeShout[len(marketTypeShout)-1]==-1):
					#bear
					if(len(quoteBase_close)%actionPeriod==0):
						if(len(rsiShout)>0):
							print "RSI:",rsiValue[len(rsiValue)-1]
						if(len(macdShout)>0):
							print "MACD:",macdValue[len(macdValue)-1]
							print "Histo:",macdHisto[len(macdHisto)-1]
						print "Bear Market"
						print "Price:",str(quoteBase_close[len(quoteBase_close)-1])
						print "Account Balance (Quote):",str(accountBalanceQuote)
						print "Account Balance (Base):",str(accountBalanceBase)
						print "Account Balance Total (Base):",str(accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1]))
						if(len(macdShout)>0 and len(rsiShout)>0):
							if(macdShout[len(macdShout)-1]==1 and rsiShout[len(rsiShout)-1]==1):
								print "Buy Bear"
								Buy()
								print "Bear Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceQuote=accountBalanceQuote+quoteTransactionAmount
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)
							elif(macdShout[len(macdShout)-1]==-1 and rsiShout[len(rsiShout)-1]==-1 and amountBuyQuote>0):
								print "Sell Bear"
								Sell()
								print "Bear Market"
								print "Price:"+str(quoteBase_close[len(quoteBase_close)-1])
								print "Kelly:"+str(kellyCoeff)
								#accountBalanceBase=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
							#	accountBalanceQuote=0
								totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
								print "Account Balance (Quote):"+str(accountBalanceQuote)
								print "Account Balance (Base):"+str(accountBalanceBase)
								print "Account Balance Total (Base):"+str(totalAccount)
			else:
				print "Markettype Not Ready"
	else:
		print "END!"
		print "Account Balance (Quote):",accountBalanceQuote
		print "Account Balance (Base):",accountBalanceBase
		sendNotification("Backtest Done!","Backtest Run Done!")
		sys.exit("All Done!")
	#	print "No New Data"

	totalAccount=accountBalanceBase+(accountBalanceQuote*quoteBase_close[len(quoteBase_close)-1])
	if(len(quoteBase_close)==1):
		stopPercent=stopPercent*totalAccount
		#print stopPercent
	if(len(quoteBase_close)>0):
		if(totalAccount<=minAmount or totalAccount<=stopPercent):
			sendNotification("Stopped","Error\nBot Stopped:RIP Money")
			sys.exit("RIP Money")
