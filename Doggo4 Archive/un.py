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

reading=False
bought=False
run=True

##Settings
pair='ETHBTC'
base="BTC"
quote="ETH"
kellyLength=60 #has to be 60
lengthTime=20160
timeCancel=10
rsiPeriod=5
atrPeriod=5
macDFastLength=10080
macDSlowLength=lengthTime
macDSignalLength=12960
file="/Users/ryan/Desktop/doggo4/Klines"
resultFile="/Users/ryan/Desktop/doggo4/trades"
maxPercent=1
minPercent=0.1
minAmount=0.001
stopPercent=0.1
gmail_user = 'doggo4notification@gmail.com'  
gmail_password = 'doggo4notify'
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']

ethbtc_close=np.array([])
ethbtc_high=np.array([])
ethbtc_low=np.array([])

avgGainRSI=0#needs to persist, global
avgLossRSI=0

rsi=np.array([])
cci=np.array([])
macD=np.array([])
macDSignal=np.array([])
macDHisto=np.array([])
atr=np.array([])
difference=np.array([])
kellyCoeff=1.0
#orderNumber=0

amountQuote=0
amountBase=0

accountBalance=0 #ETH
accountBalanceBTC=0

tradeID=np.array([])
tradeTime=0

buyAmount=0 #Kelly
sellAmount=0 #Kelly
buyPrice=np.array([]) #ATR

rsiReady=False
cciReady=False
macDReady=False
atrReady=False
kellyReady=False

rsiBuy=0
cciBuy=0
macDBuy=0
atrBuy=0

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
		msg='Subject:{}\n\n'+mesg
		msg=msg.format(subject)
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
		#newClientOrderId=str(oID),
		newOrderRespType="FULL",
		recvWindow=1000)
	return order

def Sell(amount):
	order = client.order_market_sell(
		symbol=pair,
		quantity=amount,
		#newClientOrderId=str(oID),
		newOrderRespType="FULL",
		recvWindow=1000)
	return order

def cciFunc():
	global cciBuy
	global cciReady
	global cci
	cciBuy=0
	cciReady=False
	if(len(ethbtc_close)==lengthTime and len(ethbtc_high)==lengthTime and len(ethbtc_low)==lengthTime):
		tempcci=talib.CCI(ethbtc_high,ethbtc_low,ethbtc_close,timeperiod=lengthTime)
		cci=np.append(cci,tempcci[len(tempcci)-1])
		if(len(cci)>=2):
			cciReady=True
	else:
		cciReady=False
	if(cciReady):
		cciBuy=0
		#print "CCI",cci[len(cci)-1]
		if(cci[len(cci)-2]>100):
	 		if(cci[len(cci)-1]<cci[len(cci)-2]):#curve down
				cciBuy=-1
		if(cci[len(cci)-2]<=100):
			if(cci[len(cci)-1]>cci[len(cci)-2]):
				cciBuy=1
		if(cci[len(cci)-2]<0):
			if(cci[len(cci)-1]>0):
				cciBuy=1
		if(cci[len(cci)-2]>0):
			if(cci[len(cci)-1]<0):
				cciBuy=-1
def rsiFunc():
	global rsiBuy
	global avgGainRSI
	global avgLossRSI
	global rsi
	global rsiReady
	rsiReady=False
	rsiBuy=0
	rs=0
	change=0
	currentGains=0
	currentLosses=0
	if(len(ethbtc_close)==rsiPeriod):
		tempGain=0
		tempLoss=0
		for x in range(0, rsiPeriod-2):
		 	change=ethbtc_close[x+1]-ethbtc_close[x]
		 	if(change>0):
		 		tempGain=tempGain+change
		 	elif(change<0):
		 		tempLoss=tempLoss+abs(change)
		avgGainRSI=tempGain/rsiPeriod
		avgLossRSI=tempLoss/rsiPeriod
	 	rs = avgGainRSI/avgLossRSI
		rsi=np.append(rsi,100-(100/(1+rs)))
		rsiReady=True
	elif(len(ethbtc_close)>rsiPeriod):
		change=ethbtc_close[len(ethbtc_close)-1]-ethbtc_close[len(ethbtc_close)-2]
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
		rsi=np.append(rsi,100-(100/(1+rs)))
		rsiReady=True
	else:
		rsiReady=False

	if(rsiReady):
		rsiBuy=0
		#print "RSI",rsi[len(rsi)-1]
		if(rsi[len(rsi)-1]<=30):
	 		rsiBuy=1
	 	if(rsi[len(rsi)-1]>=70):
	 		rsiBuy=-1

#TODO CHANGE MACDPERIODS TO 7,14,9 DAY MINUTE EQUIVLANTS
def macDFunc():
	global macDBuy
	global macDReady
	global macD,macDSignal,macDHisto
	macDReady=False
	macDBuy=0

	tempArray=np.array([])
	temp3=np.array([])
	temp6=np.array([])
	temp9=np.array([])

	if(len(ethbtc_close)>=lengthTime):
		#update timeperiod AND len(etbtcclose)+1
		tempArray=ethbtc_close[len(ethbtc_close)-macDFastLength:len(ethbtc_close)]
		tempFast=talib.EMA(tempArray,timeperiod=macDFastLength)

		tempArray=ethbtc_close[len(ethbtc_close)-macDSignalLength:len(ethbtc_close)]
		tempSignal=talib.EMA(tempArray,timeperiod=macDSignalLength)

		tempArray=ethbtc_close[len(ethbtc_close)-macDSlowLength:len(ethbtc_close)]
		tempSlow=talib.EMA(tempArray,timeperiod=macDSlowLength)

		emaFast=tempFast[len(tempFast)-1]
		emaSignal=tempSignal[len(tempSignal)-1]
		emaSlow=tempSlow[len(tempSlow)-1]

		macD=np.append(macD,emaFast-emaSlow)
		macDSignal=np.append(macDSignal,emaSignal)
		macDHisto=np.append(macDHisto,macD[len(macD)-1]-macDSignal[len(macDSignal)-1])
		if(len(macDHisto)>=2 and len(macD)>=2):		
			macDReady=True
	else:
		macDReady=False

	if(macDReady):
		macDBuy=0
		#print "macD", macD[len(macD)-1]
		#print "Signal",macDSignal[len(macDSignal)-1]
		#print "Histo",macDHisto[len(macDHisto)-1]
		if(macDHisto[len(macDHisto)-2]>macD[len(macD)-2]):
			if(macDHisto[len(macDHisto)-1]<=macD[len(macD)-1]):
				macDBuy=-1
		if(macDHisto[len(macDHisto)-2]<macD[len(macD)-2]):
			if(macDHisto[len(macDHisto)-1]>=macD[len(macD)-1]):
				macDBuy=1

def atrFunc():
	global atrBuy
	global atrReady
	global atr
	global lowerStop
	atrReady=False
	atrBuy=0
	tr=0
	if(len(ethbtc_close)==atrPeriod and len(ethbtc_high)==atrPeriod and len(ethbtc_low)==atrPeriod):
		for x in range(0, atrPeriod-1):
			if(ethbtc_high[x]-ethbtc_low[x]>0):
				tr=tr+abs(ethbtc_high[x]-ethbtc_low[x])
		firstAtr=tr/atrPeriod
		atr=np.append(atr,firstAtr)
		atrReady=True
	elif(len(ethbtc_close)>atrPeriod):
		if(ethbtc_high[len(ethbtc_high)-1]-ethbtc_low[len(ethbtc_low)-1]<0):
			tr=0
		else:
			tr=ethbtc_high[len(ethbtc_high)-1]-ethbtc_low[len(ethbtc_low)-1]
		prior=atr[len(atr)-1]
		atr=np.append(atr,((prior*(atrPeriod-1))+tr)/atrPeriod) #13 14, atrperiod -1?
		atrReady=True
	else:
		atrReady=False

	if(atrReady and len(buyPrice)>0):
		#print "ATR",atr[len(atr)-1]
		if(ethbtc_close[len(ethbtc_close)-1]>buyPrice[len(buyPrice)-1]):
			lowerStop=ethbtc_close[len(ethbtc_close)-1]-(2*atr[len(atr)-1])
		else:
			lowerStop=buyPrice[len(buyPrice)-1]-(2*atr[len(atr)-1])
		if(ethbtc_close[len(ethbtc_close)-1]<=lowerStop):
			atrBuy=-1
def kellyFunc():
	global kellyReady
	global kellyCoeff
	global difference
	global sellAmount
	kellyReady=False
	sellAmount=amountBase/ethbtc_close[len(ethbtc_close)-1]
	difference=np.append(difference,sellAmount-buyAmount)
	if(len(difference)>kellyLength):
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


client=login()

order = client.get_order(
symbol=pair,
orderId=107311920)
print json.dumps(order)

