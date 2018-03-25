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
#TODO instead of bought, just check if we have any quote?!

reading=False
bought=False
run=True
statusChecked=False


##Settings
pair='ADAETH'
base="ETH"
quote="ADA"
kellyLength=60 #has to be 60
lengthTime=20
timeCancel=1
rsiPeriod=14
atrPeriod=14
macDFastLength=5
macDSlowLength=lengthTime
macDSignalLength=15
fileRead="/Users/ryan/Desktop/Doggo4/ADAETH"
resultFile="/Users/ryan/Desktop/Doggo4/trades"
maxPercent=0.3
minPercent=0.1
minAmount=1
precision=0
stopPercent=0.1
gmail_user = 'doggo4notification@gmail.com'  
gmail_password = 'doggo4notify'
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']

quoteBase_close=np.array([])
quoteBase_high=np.array([])
quoteBase_low=np.array([])

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

amountQuote=0

accountBalanceQuote=0 #ADA
accountBalanceBase=0 #ETH

tradeID=np.array([])
tradeTime=0

buyAmount=0 #Kelly #might need fix
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

def cciFunc():
	global cciBuy
	global cciReady
	global cci
	cciBuy=0
	cciReady=False
	if(len(quoteBase_close)==lengthTime and len(quoteBase_high)==lengthTime and len(quoteBase_low)==lengthTime):
		tempcci=talib.CCI(quoteBase_high,quoteBase_low,quoteBase_close,timeperiod=lengthTime)
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
		rsi=np.append(rsi,100-(100/(1+rs)))
		rsiReady=True
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

def macDFunc():
	global macDBuy
	global macDReady
	global macD,macDSignal,macDHisto
	macDReady=False
	macDBuy=0

	tempArray=np.array([])
	tempFast=np.array([])
	tempSignal=np.array([])
	tempSlow=np.array([])

	if(len(quoteBase_close)>=lengthTime):
		#update timeperiod AND len(etbtcclose)+1
		tempArray=quoteBase_close[len(quoteBase_close)-macDFastLength:len(quoteBase_close)]
		tempFast=talib.EMA(tempArray,timeperiod=macDFastLength)

		tempArray=quoteBase_close[len(quoteBase_close)-macDSignalLength:len(quoteBase_close)]
		tempSignal=talib.EMA(tempArray,timeperiod=macDSignalLength)

		tempArray=quoteBase_close[len(quoteBase_close)-macDSlowLength:len(quoteBase_close)]
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
	if(len(quoteBase_close)==atrPeriod and len(quoteBase_high)==atrPeriod and len(quoteBase_low)==atrPeriod):
		for x in range(0, atrPeriod-1):
			if(quoteBase_high[x]-quoteBase_low[x]>0):
				tr=tr+abs(quoteBase_high[x]-quoteBase_low[x])
		firstAtr=tr/atrPeriod
		atr=np.append(atr,firstAtr)
		atrReady=True
	elif(len(quoteBase_close)>atrPeriod):
		if(quoteBase_high[len(quoteBase_high)-1]-quoteBase_low[len(quoteBase_low)-1]<0):
			tr=0
		else:
			tr=quoteBase_high[len(quoteBase_high)-1]-quoteBase_low[len(quoteBase_low)-1]
		prior=atr[len(atr)-1]
		atr=np.append(atr,((prior*(atrPeriod-1))+tr)/atrPeriod) #13 14, atrperiod -1?
		atrReady=True
	else:
		atrReady=False

	if(atrReady and len(buyPrice)>0):
		#print "ATR",atr[len(atr)-1]
		if(quoteBase_close[len(quoteBase_close)-1]>buyPrice[len(buyPrice)-1]):
			lowerStop=quoteBase_close[len(quoteBase_close)-1]-(2*atr[len(atr)-1])
		else:
			lowerStop=buyPrice[len(buyPrice)-1]-(2*atr[len(atr)-1])
		if(quoteBase_close[len(quoteBase_close)-1]<=lowerStop):
			atrBuy=-1
def kellyFunc():
	global kellyReady
	global kellyCoeff
	global difference
	global sellAmount
	kellyReady=False
	sellAmount=amountQuote
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

f=open(fileRead+".txt","r")
out=open(fileRead+"tmp.txt","w")
data=f.readlines()
print "Datapoints:",len(data)
if((len(data)-lengthTime)>0):
	newData=np.array([])
	for x in range(len(data)-lengthTime,len(data)):
		out.write(data[x])
	f.close()
	out.close()
	os.remove(fileRead+".txt")
	os.rename(fileRead+"tmp.txt", fileRead+".txt")
client=login()
datafile=open(fileRead+".txt","r")    
tradefile=open(resultFile+".txt","a")
accountStringQuote=json.dumps(client.get_asset_balance(quote))
accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
accountStringBase=json.dumps(client.get_asset_balance(base))
accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
sendNotification("Started","Bot Started:May The Odds Be Ever In Your Favor")
while run:
	#if(accountBalanceQuote>=minAmount):
		#bought=True
	if(len(quoteBase_close)==1):
		stopPercent=stopPercent*((accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])+accountBalanceQuote)
	if(len(quoteBase_close)>0):
		if((accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])+accountBalanceQuote<=minAmount or (accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])+accountBalanceQuote<=stopPercent):
			sendNotification("Stopped","Error\nBot Stopped:RIP Money")
			sys.exit("RIP Money")
	if(time.time()-tradeTime>=timeCancel*60 and len(tradeID)>0 and statusChecked==False):
		print "Checking Status"
		try:
			status=client.get_order(
				symbol=pair,
				orderId=int(tradeID[len(tradeID)-1]))
			tempStat=json.dumps(status)
			print tempStat
			checkStat=tempStat[tempStat.find("status")+10]
			print checkStat
		except Exception as e:
			sendNotification("Stopped","Error\nBot Stopped:Order Status Failed\n"+str(e))
			print "Error Occured While Checking:",str(e)
			sys.exit("Error Occured While Checking")
		if(checkStat!="F"):
			try:
				client.cancel_order(
				symbol=pair,
				orderId=int(tradeID[len(tradeID)-1]))
			except Exception as e:
				sendNotification("Stopped","Error\nBot Stopped:Cancel Failed\n"+str(e))
				print "Error Occured While Canceling:",str(e)
				sys.exit("Error Occured While Canceling")
		statusChecked=True
	
	#fetch
	where=datafile.tell()
	line=datafile.readline()
	reading=False
	if not line:
		reading=False
		datafile.seek(where)
	else:
		reading=True
		quoteBase_high=np.append(quoteBase_high,float(line[32:42]))
		quoteBase_low=np.append(quoteBase_low,float(line[46:56]))
		quoteBase_close=np.append(quoteBase_close,float(line[60:70]))
		if(len(quoteBase_close)>lengthTime):
			quoteBase_close=np.delete(quoteBase_close,0) #has to be numpy, talib wants numpy
		if(len(quoteBase_high)>lengthTime):
			quoteBase_high=np.delete(quoteBase_high,0) #has to be numpy, talib wants numpy
		if(len(quoteBase_low)>lengthTime):
			quoteBase_low=np.delete(quoteBase_low,0) #has to be numpy, talib wants numpy

	#update indicators
	if(reading):
		rsiFunc()
		#macDFunc()
		#cciFunc()
		atrFunc()
		if(rsiReady and atrReady and len(quoteBase_close)>=lengthTime):
			if(atrBuy==-1 and bought==True):
				#TODO what if buying/selling less than min amount. DO we cancel?
				bought=False
				atrBuy=0
				rsiBuy=0
				print "\n\n"
				print "Stoploss"
				amountQuote=accountBalanceQuote
				print math.trunc(amountQuote)
				if(amountQuote<=minAmount):
					sendNotification("Stopped","Selling Less Than Min Amount")
					sys.exit("Selling Less Than Min Amount")
				try:
					tradeResult=json.dumps(Sell(math.trunc(amountQuote)))
					tradeTime=time.time()
					statusChecked=False
					tradefile.write(tradeResult+"\n")
					tradeID=np.append(tradeID,int(tradeResult[12:20]))
				except Exception as e:
					sendNotification("Stopped","Error\nBot Stopped:Sell Failed\n"+str(e))
				   	print "Error Occured While Selling:",str(e)
					sys.exit("Error Occured While Selling")
				accountStringQuote=json.dumps(client.get_asset_balance(quote))
				accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
				accountStringBase=json.dumps(client.get_asset_balance(base))
				accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
				msg="\nATR:"+str(atr[len(atr)-1]) + \
   	 			"\nPrice:"+str(quoteBase_close[len(quoteBase_close)-1]) + \
   	 			"\nBuy Price:"+str(buyPrice[len(buyPrice)-1]) + \
     			"\nLower Limit:"+str(lowerStop) + \
     			"\nAmount Sold (Quote):"+str(amountQuote) + \
     			"\nAccount Balance (Quote):"+str(accountBalanceQuote) + \
     			"\nAccount Balance (Base):"+str(accountBalanceBase)
				print msg
				print "\n\n"
				kellyFunc()
				sendNotification("Selling Stoploss",msg)
			elif(rsiBuy==1 and bought==False):
				bought=True
				atrBuy=0
				rsiBuy=0
				#macDBuy=0
				#cciBuy=0
				if(kellyReady):
					amountQuote=kellyCoeff*maxPercent*(accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])
				else:
					amountQuote=minPercent*(accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])
				if(amountQuote<minAmount):
					amountQuote=minAmount
				if(amountQuote>=(maxPercent*accountBalanceQuote)):
					amountQuote=maxPercent*(accountBalanceBase/quoteBase_close[len(quoteBase_close)-1])
				print "\n\n"
				print "Buy Quote"
				#print round(Decimal(amountQuote),precision)
				print math.trunc(amountQuote)
				try:
					tradeResult=json.dumps(Buy(math.trunc(amountQuote)))
					tradeTime=time.time()
					statusChecked=False
					tradefile.write(tradeResult+"\n")
					tradeID=np.append(tradeID,int(tradeResult[12:20]))
				except Exception as e:
				 	sendNotification("Stopped","Error\nBot Stopped:Buy Failed\n"+str(e))
				   	print "Error Occured While Buying:",str(e)
				   	sys.exit("Error Occured While Buying")
				accountStringQuote=json.dumps(client.get_asset_balance(quote))
				accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
				accountStringBase=json.dumps(client.get_asset_balance(base))
				accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
				msg="\nRSI:"+str(rsi[len(rsi)-1]) + \
   	 			"\nPrice:"+str(quoteBase_close[len(quoteBase_close)-1]) + \
     			"\nKelly:"+str(kellyCoeff) + \
     			"\nAmount Bought (Base):"+str(accountBalanceBase) + \
     			"\nAccount Balance (Quote):"+str(accountBalanceQuote) + \
     			"\nAccount Balance (Base):"+str(accountBalanceBase)
				# print "RSI:",rsi[len(rsi)-1]
				# print "CCI:",cci[len(cci)-1]
				# print "macD:",macD[len(macD)-1]
				# print "Histo:",macDHisto[len(macDHisto)-1]
				# print "Kelly:",kellyCoeff
				print msg
				print "\n\n"
				buyAmount=amountQuote
				buyPrice=np.append(buyPrice,quoteBase_close[len(quoteBase_close)-1]) #atr
				sendNotification("Buying",msg)
			elif(rsiBuy==-1 and bought==True):
				bought=False
				atrBuy=0
				rsiBuy=0
				#cciBuy=0
				#macDBuy=0
				amountQuote=accountBalanceQuote
				print math.trunc(amountQuote)
				print "\n\n"
				print "Sell Quote"
				try:
					tradeResult=json.dumps(Sell(math.trunc(amountQuote)))
					tradeTime=time.time()
					statusChecked=False
					tradefile.write(tradeResult+"\n")
					tradeID=np.append(tradeID,int(tradeResult[12:20]))
				except Exception as e:
				 	sendNotification("Stopped","Error\nBot Stopped:Sell Failed\n"+str(e))
				  	print "Error Occured While Selling:",str(e)
				 	sys.exit("Error Occured While Selling")
				accountStringQuote=json.dumps(client.get_asset_balance(quote))
				accountBalanceQuote=float(accountStringQuote[12:22])+float(accountStringQuote[50:60])
				accountStringBase=json.dumps(client.get_asset_balance(base))
				accountBalanceBase=float(accountStringBase[12:22])+float(accountStringBase[50:60])
				msg="\nRSI:"+str(rsi[len(rsi)-1]) + \
   	 			"\nPrice:"+str(quoteBase_close[len(quoteBase_close)-1]) + \
     			"\nKelly:"+str(kellyCoeff) + \
     			"\nAmount Sold (Quote):"+str(amountQuote) + \
     			"\nAccount Balance (Quote):"+str(accountBalanceQuote) + \
     			"\nAccount Balance (Base):"+str(accountBalanceBase)
				# print "RSI:",rsi[len(rsi)-1]
				# print "CCI:",cci[len(cci)-1]
				# print "macD:",macD[len(macD)-1]
				# print "Histo:",macDHisto[len(macDHisto)-1]
				# print "Kelly:",kellyCoeff
				print msg
				print "\n\n"
				kellyFunc()
				sendNotification("Selling",msg)
		else:
			print "Not Ready. We Need ",lengthTime-len(quoteBase_close)," More Data Points"
		if(len(quoteBase_close)>=lengthTime):
			if(reading):
				print "Info Updated:",datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")
				print "RSI:",rsi[len(rsi)-1]
				#print "CCI:",cci[len(cci)-1]
				#print "macD:",macD[len(macD)-1]
				#print "Histo:",macDHisto[len(macDHisto)-1]
				print "Kelly:",kellyCoeff