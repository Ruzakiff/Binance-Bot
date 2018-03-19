from binance.client import Client
import numpy as np
import config
import sys
import time
import talib
import json

reading=False
bought=False
run=True

kellyLength=60 #has to be 60
lengthTime=12960

ethbtc_close=np.array([])
ethbtc_high=np.array([])
ethbtc_low=np.array([])

avgGainRSI=0#needs to persist, global
avgLossRSI=0

rsi=np.array([])
cci=np.array([])
macD=np.array([])
signal=np.array([])
macDHisto=np.array([])
atr=np.array([])
difference=np.array([])
kellyCoeff=1.0

amountETH=0
amountBTC=0

accountBalance=3


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

counter=1

def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client

def Buy(amount):
	order = client.order_market_buy(
		symbol="BTC",
		quantity=amount)

def Sell(amount):
	order = client.order_market_sell(
		symbol="BTC",
		quantity=amount)

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
	##maybe place this first? no lag behind	
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
	if(len(ethbtc_close)==14):
		tempGain=0
		tempLoss=0
		for x in range(0, 12):
		 	change=ethbtc_close[x+1]-ethbtc_close[x]
		 	if(change>0):
		 		tempGain=tempGain+change
		 	elif(change<0):
		 		tempLoss=tempLoss+abs(change)
		avgGainRSI=tempGain/14
		avgLossRSI=tempLoss/14
	 	rs = avgGainRSI/avgLossRSI
		rsi=np.append(rsi,100-(100/(1+rs)))
		rsiReady=True
	elif(len(ethbtc_close)>14):
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
		avgGainRSI=(13*avgGainRSI + currentGains)/14 #this is setting avggain and loss that is from intialize. values persist
		avgLossRSI=(13*avgLossRSI + currentLosses)/14
		rs = avgGainRSI/avgLossRSI
		rsi=np.append(rsi,100-(100/(1+rs)))
		rsiReady=True
	else:
		rsiReady=False

	if(rsiReady):
		rsiBuy=0
		#print "RSI",rsi[len(rsi)-1]
		if(rsi[len(rsi)-1]<=25):
	 		rsiBuy=1
	 	if(rsi[len(rsi)-1]>=60):
	 		rsiBuy=-1

#TODO CHANGE MACDPERIODS TO 7,14,9 DAY MINUTE EQUIVLANTS
def macDFunc():
	global macDBuy
	global macDReady
	global macD,signal,macDHisto
	macDReady=False
	macDBuy=0

	tempArray=np.array([])
	temp3=np.array([])
	temp6=np.array([])
	temp9=np.array([])

	if(len(ethbtc_close)>=12960):
		tempArray=ethbtc_close[len(ethbtc_close)-4321:len(ethbtc_close)]
		temp3=talib.EMA(tempArray,timeperiod=4320)

		tempArray=ethbtc_close[len(ethbtc_close)-8641:len(ethbtc_close)]
		temp6=talib.EMA(ethbtc_close,timeperiod=8640)
#ethbc close? or temp array wut
#tempa
		tempArray=ethbtc_close[len(ethbtc_close)-12961:len(ethbtc_close)]
		temp9=talib.EMA(tempArray,timeperiod=12960)

		ema3=temp3[len(temp7)-1]
		ema6=temp6[len(temp9)-1]
		ema9=temp9[len(temp14)-1]

		macD=np.append(macD,ema3-ema9)
		signal=np.append(signal,ema6)
		macDHisto=np.append(macDHisto,macD[len(macD)-1]-signal[len(signal)-1])
		if(len(macDHisto)>=2 and len(macD)>=2):		
			macDReady=True
	else:
		macDReady=False

	if(macDReady):
		macDBuy=0
		#print "macD", macD[len(macD)-1]
		#print "Signal",signal[len(signal)-1]
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
	if(len(ethbtc_close)==14 and len(ethbtc_high)==14 and len(ethbtc_low)==14):
		for x in range(0, 13):
			if(ethbtc_high[x]-ethbtc_low[x]>0):
				tr=tr+abs(ethbtc_high[x]-ethbtc_low[x])#no negative
		firstAtr=tr/14
		atr=np.append(atr,firstAtr)
	elif(len(ethbtc_close)>14):
		if(ethbtc_high[len(ethbtc_high)-1]-ethbtc_low[len(ethbtc_low)-1]<0):
			tr=0
		else:
			tr=ethbtc_high[len(ethbtc_high)-1]-ethbtc_low[len(ethbtc_low)-1]
		prior=atr[len(atr)-1]
		atr=np.append(atr,((prior*13)+tr)/14)
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


client=login()
datafile=open("/Users/ryan/Desktop/doggo4/Klines.txt","r")
accountString=json.dumps(client.get_asset_balance("ETH"))
accountBalance=float(accountString[12:22])+float(accountString[50:60])
while run:
	if(accountBalance<=0):
		sys.exit("RIP Money")
	#print "\nLoop:",counter
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
		print "Kelly:",kellyCoeff
		if(rsiReady and atrReady and cciReady and macDReady):
			if(atrBuy==-1 and bought==True):
				bought=False
				atrBuy=0
				rsiBuy=0
				print "STOP"
				print "ATR:",atr[len(atr)-1]
				print "Price:",ethbtc_close[len(ethbtc_close)-1]
				print "Buy Price:",buyPrice[len(buyPrice)-1]
				print "Lower Limit:",lowerStop
				Sell(amountBTC)
				print "Amount Sold (BTC):",amountBTC
				accountString=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountString[12:22])+float(accountString[50:60])
				#accountBalance=accountBalance+(amountBTC/ethbtc_close[len(ethbtc_close)-1])
				print "Account Balance (ETH):",accountBalance
				#kelly
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

			elif(rsiBuy==1 and macDBuy==1 and cciBuy==1 and bought==False):
				bought=True
				rsiBuy=0
				macDBuy=0
				cciBuy=0
				if(kellyReady):
					amountETH=kellyCoeff*0.333*accountBalance
				else:
					amountETH=0.10*accountBalance
				if(amountETH>=(0.333*accountBalance)or amountETH<0):
					amountETH=0.1*accountBalance
				amountBTC=amountETH*ethbtc_close[len(ethbtc_close)-1]
				print "Buy"
				print "RSI:",rsi[len(rsi)-1]
				print "CCI:",cci[len(cci)-1]
				print "macD:",macD[len(macD)-1]
				print "Histo:"macDHisto[len(macDHisto)-1]
				print "Kelly:",kellyCoeff
				Buy(amountBTC)
				print "Amount Bought (BTC):",amountBTC
				accountString=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountString[12:22])+float(accountString[50:60])
				#accountBalance=accountBalance-amountETH
				print "Account Balance (ETH):",accountBalance
				#print "Kelly:",kellyCoeff
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
				print "Histo:"macDHisto[len(macDHisto)-1]
				print "Kelly:",kellyCoeff
				Sell(amountBTC)
				print "Amount Sold (BTC):",amountBTC
				accountString=json.dumps(client.get_asset_balance("ETH"))
				accountBalance=float(accountString[12:22])+float(accountString[50:60])
				#accountBalance=accountBalance+(amountBTC/ethbtc_close[len(ethbtc_close)-1])
				print "Account Balance (ETH):",accountBalance
				#kelly
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
					#	print "Kelly:",kellyCoeff
						kellyReady=True
					except:
						sys.exit("Divide By 0")
				else:
					kellyReady=False
		else:
			print "Not Ready. We Need ",lengthTime-len(ethbtc_close)," More Data Points"
		#counter=counter+1
