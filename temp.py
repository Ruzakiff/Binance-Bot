from binance.client import Client
import numpy as np
import time
import talib
import sys
import config
rsiBuy=0
macDBuy=0
cciBuy=0
atrSell=False

rsi=np.array([])
cci=np.array([])
macD=np.array([])
signal=np.array([])
macDHisto=np.array([])
atr=np.array([])
upperStop=np.array([])
lowerStop=0
kellyCoeff=1
kellyLength=60

amountETH=0
amountBTC=0
buyValue=np.array([])
sellValue=np.array([])
accountBalance=3

#2880
lengthTime=28

ethbtc_close=np.array([])
ethbtc_high=np.array([])
ethbtc_low=np.array([])

reading=False
run=True

cciReady=False
macDReady=False
rsiReady=False
kellyReady=False
atrReady=False

avgGainRSI=0#needs to persist, global
avgLossRSI=0#needs to persist, global
counter=0
bought=False
buyPrice=0


def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client
def Buy(symbol,amount):
	order = client.order_market_buy(
		symbol=symbol,
		quantity=amount)
def Sell(symbol,amount):
	order = client.order_market_sell(
		symbol=symbol,
		quantity=amount)



def cciFunc():
	global cciBuy
	global cciReady
	global cci
	cciBuy=0
	if(len(ethbtc_close)==lengthTime and len(ethbtc_high)==lengthTime and len(ethbtc_low)==lengthTime):
		tempcci=talib.CCI(ethbtc_high,ethbtc_low,ethbtc_close,timeperiod=lengthTime)
		cci=np.append(cci,tempcci[len(tempcci)-1])
		if(len(cci)>=2):
			cciReady=True
	else:
		cciReady=False
	##maybe place this first? no lag behind	
	if(cciReady):
		print "CCI",cci[len(cci)-1]
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
		print "RSI",rsi[len(rsi)-1]
		if(rsi[len(rsi)-1]<=30):
	 		rsiBuy=1
	 	if(rsi[len(rsi)-1]>=70):
	 		rsiBuy=-1
#TODO CHANGE MACDPERIODS TO 7,14,9 DAY MINUTE EQUIVLANTS	 		
def macDFunc():
	global macDBuy
	global macDReady
	global macD,signal,macDHisto
	macDBuy=0

	tempArray=np.array([])
	temp7=np.array([])
	temp9=np.array([])
	temp14=np.array([])

	if(len(ethbtc_close)>=14):
		tempArray=ethbtc_close[len(ethbtc_close)-8:len(ethbtc_close)]
		temp7=talib.EMA(tempArray,timeperiod=7)

		tempArray=ethbtc_close[len(ethbtc_close)-10:len(ethbtc_close)]
		temp9=talib.EMA(ethbtc_close,timeperiod=9)

		tempArray=ethbtc_close[len(ethbtc_close)-15:len(ethbtc_close)]
		temp14=talib.EMA(ethbtc_close,timeperiod=14)

		ema7=temp7[len(temp7)-1]
		ema9=temp9[len(temp9)-1]
		ema14=temp14[len(temp14)-1]

		macD=np.append(macD,ema7-ema14)
		signal=np.append(signal,ema9)
		macDHisto=np.append(macDHisto,macD[len(macD)-1]-signal[len(signal)-1])
		if(len(macDHisto)>=2 and len(macD)>=2):		
			macDReady=True
	else:
		macDReady=False

	if(macDReady):
		print "macD", macD[len(macD)-1]
		print "Signal",signal[len(signal)-1]
		print "Histo",macDHisto[len(macDHisto)-1]
		if(macDHisto[len(macDHisto)-2]>macD[len(macD)-2]):
			if(macDHisto[len(macDHisto)-1]<=macD[len(macD)-1]):
				macDBuy=-1
		if(macDHisto[len(macDHisto)-2]<macD[len(macD)-2]):
			if(macDHisto[len(macDHisto)-1]>=macD[len(macD)-1]):
				macDBuy=1

def kellyFunc():
	global kellyCoeff
	global kellyReady
	global buyValue
	global sellValue
	if(len(buyValue)>kellyLength):
		buyValue=np.delete(buyValue,0)
	if(len(sellValue)>kellyLength):
		sellValue=np.delete(sellValue,0)
		
	if(len(buyValue)==kellyLength and len(sellValue)==kellyLength):
		kellyReady=True
	else:
		kellyReady=False
def atrFunc():
	global atrSell
	global atrReady
	global atr
	global buyPrice
	global lowerStop
	tr=0
	if(len(ethbtc_close)==14 and len(ethbtc_high)==14 and len(ethbtc_low)==14):
		for x in range(0, 13):
			if(ethbtc_high[x]-ethbtc_low[x]>0):
				tr=tr+abs(ethbtc_high[x]-ethbtc_low[x])#no negative
		firstAtr=tr/14
		atr=np.append(atr,firstAtr)
		atrReady=True
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
	if(atrReady):
		print "ATR",atr[len(atr)-1]
		if(ethbtc_close[len(ethbtc_close)-1]>buyPrice):
			lowerStop=ethbtc_close[len(ethbtc_close)-1]-(2*atr[len(atr)-1])
		else:
			lowerStop=buyPrice-(2*atr[len(atr)-1])
		
#main
client=login()
datafile=open("/Users/ryan/Desktop/doggo4/Klines.txt", "r")
while run:
	print "\n\nLoop:",counter
	where = datafile.tell()
	line = datafile.readline()
	reading
	if not line:
		reading=False
		datafile.seek(where)
	else:
		reading=True
		#print line
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
		#macDFunc()
		#cciFunc()
		kellyFunc()
		atrFunc()
		print atrSell

		if(rsiReady and atrReady): #if(rsiReady and cciReady and macDReady):
			#print "Indicators Ready"		
			price=ethbtc_close[len(ethbtc_close)-1]
			if(kellyCoeff<0):
				print "urbad"
				kellyCoeff=0.1
			#if(cciBuy==0 or rsiBuy==0):
				#print "Not Doing Anything"

			if(rsiBuy==1 and bought==False):
			#if(cciBuy==1 and rsiBuy==1 and macDBuy==1):
				#run=False
				cciBuy=0
				rsiBuy=0
				amountETH=kellyCoeff*0.333*accountBalance
				amountBTC=amountETH*price
				buyPrice=price
				print "Buying:",price
				print "Kelly:",kellyCoeff
				print "Amount In BTC:",amountBTC
				accountBalance=accountBalance-amountETH
				print "Account In ETH:",accountBalance
				buyValue=np.append(buyValue,amountBTC/price)
				bought=True
			if(bought==True and rsiBuy==-1):
			#if(cciBuy==-1 and rsiBuy==-1 and macDBuy==-1):
				bought=False
				cciBuy=0
				rsiBuy=0
				#bought=False
				print "Selling:",price
				print "Kelly:",kellyCoeff
				print "Amount In BTC:",amountBTC
				accountBalance=accountBalance+(amountBTC/price)
				print "Account In ETH:",accountBalance
				#bought=False
				sellValue=np.append(sellValue,amountBTC/price)
				if(kellyReady):
					gains=0
					losses=0
					gainCount=0
					lossCount=0
					avgGainKelly=0
					avgLossKelly=0
					try:
						for x in range(0,kellyLength):
							diff=sellValue[x]-buyValue[x]
							if(diff>0):
								gains=gains+diff
								gainCount=gainCount+1
							if(diff<0):
								losses=losses+abs(diff)
								lossCount=lossCount+1
						avgGainKelly=gains/gainCount
						avgLossKelly=losses/lossCount
						temp=gainCount/lossCount
						kellyCoeff=(temp)-((1-temp)/(avgGainKelly/avgLossKelly))
					except:
						sys.exit("No Gains, Divide by Zero Kelly")
					else:
						continue
			if(bought==True and ethbtc_close[len(ethbtc_close)-1]<lowerStop):
				bought=False
				cciBuy=0
				rsiBuy=0
				#bought=False
				print "Selling STOP:",price
				print "Kelly:",kellyCoeff
				print "Amount In BTC:",amountBTC
				accountBalance=accountBalance+(amountBTC/price)
				print "Account In ETH:",accountBalance
				#bought=False
				sellValue=np.append(sellValue,amountBTC/price)
				if(kellyReady):
					gains=0
					losses=0
					gainCount=0
					lossCount=0
					avgGainKelly=0
					avgLossKelly=0
					try:
						for x in range(0,kellyLength):
							diff=sellValue[x]-buyValue[x]
							if(diff>0):
								gains=gains+diff
								gainCount=gainCount+1
							if(diff<0):
								losses=losses+abs(diff)
								lossCount=lossCount+1
						avgGainKelly=gains/gainCount
						avgLossKelly=losses/lossCount
						temp=gainCount/lossCount
						kellyCoeff=(temp)-((1-temp)/(avgGainKelly/avgLossKelly))
					except:
						sys.exit("No Gains, Divide by Zero Kelly")
					else:
						continue

				#bought=False
		else:
			print "Indicators Not Ready"
	#time.sleep(0.1)
	if(reading):
	#	print "asdf"
		counter=counter+1
