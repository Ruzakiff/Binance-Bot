from binance.client import Client
import numpy as np
import time
from indicators import *
#buyAmount=0
amount=0
#sellAmount=buyAmount
rsiBuy=0
macBuy=0
cciBuy=0
buyValue=np.array([])
sellValue=np.array([])
gains=0
losses=0
gainCounter=0
lossCounter=0
avgGain=0
avgLoss=0
#TODO GET ACCOUNT BALANCE
def login():
	print "Connecting..."
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client

#main
client=login();
def Buy(symbol,amount):
	order = client.order_market_buy(
		symbol=symbol,
		quantity=amount)
def Sell(symbol,amount):
	order = client.order_market_sell(
		symbol=symbol,
		quantity=amount)
while 1:
	try:#catch actual exceptions, do before actual launch
		currentPrice=ethbtc_price[len(ethbtc_price)-1]
		if(len(buyValue)==len(sellValue)):
			kelly=(gainCounter/lossCounter)-((1-(gainCounter/lossCounter))/(avgGain/avgLoss))
		amount=kelly*accountBalance
		if(rsi[len(rsi)-1]<=30):
			rsiBuy=1
			#Buy('ETHBTC',buyAmount)
		if(rsi[len(rsi)-1)>=70):
		       	rsiBuy=-1
			#Sell('ETHBTC',sellAmount)
		if(lMacD[len(lMacD)-2]>hMacD[len(hMacD)-2]:#second previous, small higher than big
		   	if(lMacD[len(lMacD)-1]<=hMacD[len(hMacD)-1):#crossed over, or at line
				macBuy=-1
				#Sell('ETHBTC',sellAmount)
		if(lMacD[len(lMacD)-2]<hMacD[len(hMacD)-2]:#second previous, small lower than big
		   	if(lMacD[len(lMacD)-1]>=hMacD[len(hMacD)-1):#crossed over, or at line
				macBuy=1
				#Buy('ETHBTC',buyAmount)
	#Possible sell signals:The CCI crosses above 100 and has started to curve downwards. 
	#Possible buy signals:The CCI crosses below -100 and has started to curve upwards.
	#signals buy if crosses zero line from - to +, sell vice versa
	#also, it most things refer to line/curve, but we are just checking previous point before (this is why we would wanna use numpy if possible to apporixmate curve)
	#which for some reason could be like really weird or outlier, so not accurate, do we care?
	#or is that what is supposed to be good, for sniping and shit (supposed to be good, stength of cci is in outliers and momentum movement)
		if(cci[len(cci)-2]>100):
			if(cci[len(cci)-1]<cci[len(cci)-2]):#curve down
				cciBuy=-1
			      	#Sell('ETHBTC',sellAmount)
		if(cci[len(cci)-2]<-100):
			if(cci[len(cci)-1>cci[len(cci)-2]):#curve up
				cciBuy=1
		       		#Buy('ETHBTC',buyAmount)
		if(cci[len(cci)-2]<0):
		       if(cci[len(cci)-1]>0):
				cciBuy=1
		       		#Buy('ETHBTC',buyAmount)
		if(cci[len(cci)-2]>0):
		       if(cci[len(cci)-1]<0):
				cciBuy=-1
	       			#Sell('ETHBTC',sellAmount)
	      	if(cciBuy==1 and rsiBuy==1 and macBuy==1):
		       		Buy('ETHBTC',amount)
		       		buyValue=np.append(buyValue,currentPrice)
		       		if(len(buyValue)>60):
					buyValue=np.delete(buyValue,0)
	       	if(cciBuy==-1 and rsiBuy==-1 and macBuy==-1):
		       		Sell('ETHBTC',amount)
		       		sellValue=np.append(sellValue,currentPrice)
			       	if(len(sellValue)>60):
		       			sellValue=np.delete(sellValue,0)
		time.sleep(1)
	except:
		print "holl up"
	else:
		print "gucci"
