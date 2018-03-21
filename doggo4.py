from binance.client import Client
import numpy as np
import config
import sys
import time
import talib
import json
import datetime
import os

reading=False
bought=False
run=True

kellyLength=60 #has to be 60
lengthTime=12960
rsiPeriod=14
atrPeriod=14
macDFastLength=4320
macDSlowLength=lengthTime
macDSignalLength=8640
file="/Users/ryan/Desktop/doggo4/Klines"
maxPercent=0.333
minPercent=0.1
stopPercent=0.1

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
orderNumber=0

amountETH=0
amountBTC=0

accountBalance=0 #ETH
accountBalanceBTC=0

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

def Buy(amount,oID):
	order = client.order_market_buy(
		symbol='ETHBTC',
		quantity=amount,
		newClientOrderId=str(oID),
		recvWindow=1000)

def Sell(amount,id):
	order = client.order_market_sell(
		symbol='ETHBTC',
		quantity=amount,
		newClientOrderId=str(oID),
		recvWindow=1000)

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
	sellAmount=amountBTC/ethbtc_close[len(ethbtc_close)-1]
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
			sys.exit("Divide By 0")
	else:
		kellyReady=False

with open(file+".txt","r") as f, open(file+"tmp.txt","w") as out:
	data=f.readlines()
	print len(data)
	if((len(data)-lengthTime)>0):
		with open(file+"tmp.txt","w") as out:
			newData=np.array([])
			for x in range(len(data)-lengthTime,len(data)):
				out.write(data[x])
			os.remove(file+".txt")
			os.rename(file+"tmp.txt", file+".txt")
client=login()
datafile=open(file+".txt","r")    
accountStringETH=json.dumps(client.get_asset_balance("ETH"))
accountBalance=float(accountStringETH[12:22])+float(accountStringETH[50:60])
accountStringBTC=json.dumps(client.get_asset_balance("BTC"))
accountBalanceBTC=float(accountStringBTC[12:22])+float(accountStringBTC[50:60])
stopPercent=stopPercent*accountBalance
while run:
	if(accountBalance<=stopPercent):
		sys.exit("RIP Money")
	#fetch
	where=datafile.tell()
	line=datafile.readline()
	reading=False
	if not line:
		reading=False
		datafile.seek(where)
	else:
		reading=True
		ethbtc_high=np.append(ethbtc_high,float(line[32:42]))
		ethbtc_low=np.append(ethbtc_low,float(line[46:56]))
		ethbtc_close=np.append(ethbtc_close,float(line[60:70]))
		if(len(ethbtc_close)>lengthTime):
			ethbtc_close=np.delete(ethbtc_close,0) #has to be numpy, talib wants numpy
		if(len(ethbtc_high)>lengthTime):
			ethbtc_high=np.delete(ethbtc_high,0) #has to be numpy, talib wants numpy
		if(len(ethbtc_low)>lengthTime):
			ethbtc_low=np.delete(ethbtc_low,0) #has to be numpy, talib wants numpy

	#update indicators
	if(reading):
		rsiFunc()
		macDFunc()
		cciFunc()
		atrFunc()
		if(rsiReady and atrReady and cciReady and macDReady):
			if(atrBuy==-1 and bought==True):
				bought=False
				atrBuy=0
				rsiBuy=0
				print "Stoploss"
				print "ATR:",atr[len(atr)-1]
				print "Price:",ethbtc_close[len(ethbtc_close)-1]
				print "Buy Price:",buyPrice[len(buyPrice)-1]
				print "Lower Limit:",lowerStop
				try:
				  	Sell(amountBTC)
				except Exception as e:
				  	print "Error Occured While Selling:",e
				  	sys.exit("Error Occured While Selling")
				print "Amount Sold (BTC):",amountBTC
				accountStringETH=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountStringETH[12:22])+float(accountStringETH[50:60])
				accountStringBTC=json.dumps(client.get_asset_balance("BTC"))
				accountBalanceBTC=float(accountStringBTC[12:22])+float(accountStringBTC[50:60])
				#accountBalance=accountBalance+(amountBTC/ethbtc_close[len(ethbtc_close)-1])
				print "Account Balance (ETH):",accountBalance
				print "Account Balance (BTC):",accountBalanceBTC
				kellyFunc()

			elif(rsiBuy==1 and macDBuy==1 and cciBuy==1 and bought==False):
				bought=True
				rsiBuy=0
				macDBuy=0
				cciBuy=0
				if(kellyReady):
					amountETH=kellyCoeff*maxPercent*accountBalance
				else:
					amountETH=minPercent*accountBalance
				if(amountETH<0):
					amountETH=minPercent*accountBalance
				if(amountETH>=(maxPercent*accountBalance)):
					amountETH=maxPercent*accountBalance
				amountBTC=amountETH*ethbtc_close[len(ethbtc_close)-1]
				print "Buy"
				print "RSI:",rsi[len(rsi)-1]
				print "CCI:",cci[len(cci)-1]
				print "macD:",macD[len(macD)-1]
				print "Histo:",macDHisto[len(macDHisto)-1]
				print "Kelly:",kellyCoeff
				try:
				  	Buy(amountBTC)
				except Exception as e:
				  	print "Error Occured While Buying:",e
				  	sys.exit("Error Occured While Buying")
				print "Amount Bought (BTC):",amountBTC
				accountStringETH=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountStringETH[12:22])+float(accountStringETH[50:60])
				accountStringBTC=json.dumps(client.get_asset_balance("BTC"))
				accountBalanceBTC=float(accountStringBTC[12:22])+float(accountStringBTC[50:60])
				#accountBalance=accountBalance-amountETH
				print "Account Balance (ETH):",accountBalance
				print "Account Balance (BTC):",accountBalanceBTC
				buyAmount=amountETH
				buyPrice=np.append(buyPrice,ethbtc_close[len(ethbtc_close)-1]) #atr
			elif(rsiBuy==-1 and bought==True):
				bought=False
				atrBuy=0
				rsiBuy=0
				cciBuy=0
				macDBuy=0
				print "Sell"
				print "RSI:",rsi[len(rsi)-1]
				print "CCI:",cci[len(cci)-1]
				print "macD:",macD[len(macD)-1]
				print "Histo:",macDHisto[len(macDHisto)-1]
				print "Kelly:",kellyCoeff
				try:
				 	Sell(amountBTC)
				except Exception as e:
				 	print "Error Occured While Selling:",e
					sys.exit("Error Occured While Selling")
				print "Amount Sold (BTC):",amountBTC
				accountStringETH=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountStringETH[12:22])+float(accountStringETH[50:60])
				accountStringBTC=json.dumps(client.get_asset_balance("BTC"))
				accountBalanceBTC=float(accountStringBTC[12:22])+float(accountStringBTC[50:60])
				#accountBalance=accountBalance+(amountBTC/ethbtc_close[len(ethbtc_close)-1])
				print "Account Balance (ETH):",accountBalance
				print "Account Balance (BTC):",accountBalanceBTC
				kellyFunc()
		else:
			print "Not Ready. We Need ",lengthTime-len(ethbtc_close)," More Data Points"
		if(len(ethbtc_close)>=lengthTime):
			if(reading):
				print "Info Updated:",datetime.datetime.now().strftime("%a, %d %B %Y %I:%M:%S")
