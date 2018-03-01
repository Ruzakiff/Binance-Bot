from binance.client import Client
import numpy as np
import time
import talib
import sys
import config
reading=True
amount=10
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
sma=np.array([])
ema=np.array([])
rsi=np.array([])
cci=np.array([])
#2880
lengthTime=1000
ethbtc_close=np.array([])
ethbtc_high=np.array([])
ethbtc_low=np.array([])
#TODO GET ACCOUNT BALANCE
accountBalance=1000
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


#main
client=login()
datafile=open("/Users/ryan/Desktop/doggo4/Klines.txt", "r")
while 1:
	currentBalance=client.get_asset_balance(asset="ETH")
	reading=True
	#update
	while reading:
		where = datafile.tell()
		line = datafile.readline()
		if not line:
			reading=False
			datafile.seek(where)
		else:
		#print line
			reading=True
			print line
			ethbtc_high=np.append(ethbtc_high,float(line[32:42]))
			ethbtc_low=np.append(ethbtc_low,float(line[46:56]))
			ethbtc_close=np.append(ethbtc_close,float(line[60:70]))
			if(len(ethbtc_close)>lengthTime):
				ethbtc_close=np.delete(ethbtc_close,0) #has to be numpy, talib wants numpy
			if(len(ethbtc_high)>lengthTime):
				ethbtc_high=np.delete(ethbtc_high,0) #has to be numpy, talib wants numpy
			if(len(ethbtc_low)>lengthTime):
				ethbtc_low=np.delete(ethbtc_low,0) #has to be numpy, talib wants numpy
			if(len(ethbtc_high)<lengthTime or len(ethbtc_close)<lengthTime or len(ethbtc_low)<lengthTime):
				reading=True
			else:
				reading=False
			#print ethbtc_high
		#print line[32:42]
		#print line[46:56]
		#print line[60:70]
			#print reading
    		#print len(ethbtc_close)
	
	#print "Not Reading"
	#indicators
	if(len(ethbtc_close)==lengthTime and len(ethbtc_low)==lengthTime and len(ethbtc_high)==lengthTime):
	 	#maybe infinite size closing price, reading=true only while size <lengthTime. and keep appending, no delete
	 	#or take last sma thing and append to actual sma array
	 	temprsi=talib.RSI(ethbtc_close,timeperiod=14)
	 	hMacD,mMacD,lMacD=talib.MACD(ethbtc_close,fastperiod=12, slowperiod=26, signalperiod=9)#default intervals
	 	tempcci=talib.CCI(ethbtc_high,ethbtc_low,ethbtc_close,timeperiod=lengthTime)
	 	#print temprsi
	 	##not entire rsi, just appended last cause lazy. it should be oki
	 	rsi=np.append(rsi,temprsi[len(temprsi)-1])
	 	cci=np.append(cci,tempcci[len(tempcci)-1])
	 	#print rsi
	 	if(rsi[len(rsi)-1]<=30):
	 		rsiBuy=1
	 	if(rsi[len(rsi)-1]>=70):
	 		rsiBuy=-1
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
		if(cciBuy==0 or rsiBuy==0):
			print "Not Doing Anything"
			print "cci",cci[len(cci)-1]
			print "rsi",rsi[len(rsi)-1]
		if(cciBuy==1 and rsiBuy==1):
			cciBuy=0
			rsiBuy=0
			print "Buying:",ethbtc_close[len(ethbtc_close)-1]
			print "cci",cci[len(cci)-1]
			print "rsi",rsi[len(rsi)-1]
	# 	       		Buy('ETHBTC',amount)
	# 	       		buyValue=np.append(buyValue,currentPrice)
	# 	       		if(len(buyValue)>60):
	# 				buyValue=np.delete(buyValue,0)
		if(cciBuy==-1 and rsiBuy==-1):
			cciBuy=0
			rsiBuy=0
			print "Selling:",ethbtc_close[len(ethbtc_close)-1]
			print "cci",cci[len(cci)-1]
			print "rsi",rsi[len(rsi)-1]

	# 	       		Sell('ETHBTC',amount)
	# 	       		sellValue=np.append(sellValue,currentPrice)
	# 		       	if(len(sellValue)>60):
	# 	       			sellValue=np.delete(sellValue,0)

	#execute
	# try:#catch actual exceptions, do before actual launch
	# 	currentPrice=ethbtc_price[len(ethbtc_price)-1]
	# 	if(len(buyValue)==len(sellValue)):
	# 		kelly=(gainCounter/lossCounter)-((1-(gainCounter/lossCounter))/(avgGain/avgLoss))
	# 	amount=kelly*accountBalance
	# 	if(rsi[len(rsi)-1]<=30):
	# 		rsiBuy=1
	# 		#Buy('ETHBTC',buyAmount)
	# 	if(rsi[len(rsi)-1)>=70):
	# 	       	rsiBuy=-1
	# 		#Sell('ETHBTC',sellAmount)
	# 	if(lMacD[len(lMacD)-2]>hMacD[len(hMacD)-2]:#second previous, small higher than big
	# 	   	if(lMacD[len(lMacD)-1]<=hMacD[len(hMacD)-1):#crossed over, or at line
	# 			macBuy=-1
	# 			#Sell('ETHBTC',sellAmount)
	# 	if(lMacD[len(lMacD)-2]<hMacD[len(hMacD)-2]:#second previous, small lower than big
	# 	   	if(lMacD[len(lMacD)-1]>=hMacD[len(hMacD)-1):#crossed over, or at line
	# 			macBuy=1
	# 			#Buy('ETHBTC',buyAmount)
	# #Possible sell signals:The CCI crosses above 100 and has started to curve downwards. 
	# #Possible buy signals:The CCI crosses below -100 and has started to curve upwards.
	# #signals buy if crosses zero line from - to +, sell vice versa
	# #also, it most things refer to line/curve, but we are just checking previous point before (this is why we would wanna use numpy if possible to apporixmate curve)
	# #which for some reason could be like really weird or outlier, so not accurate, do we care?
	# #or is that what is supposed to be good, for sniping and shit (supposed to be good, stength of cci is in outliers and momentum movement)
	# 	if(cci[len(cci)-2]>100):
	# 		if(cci[len(cci)-1]<cci[len(cci)-2]):#curve down
	# 			cciBuy=-1
	# 		      	#Sell('ETHBTC',sellAmount)
	# 	if(cci[len(cci)-2]<-100):
	# 		if(cci[len(cci)-1>cci[len(cci)-2]):#curve up
	# 			cciBuy=1
	# 	       		#Buy('ETHBTC',buyAmount)
	# 	if(cci[len(cci)-2]<0):
	# 	       if(cci[len(cci)-1]>0):
	# 			cciBuy=1
	# 	       		#Buy('ETHBTC',buyAmount)
	# 	if(cci[len(cci)-2]>0):
	# 	       if(cci[len(cci)-1]<0):
	# 			cciBuy=-1
	#        			#Sell('ETHBTC',sellAmount)
	#       	if(cciBuy==1 and rsiBuy==1 and macBuy==1):
	# 	       		Buy('ETHBTC',amount)
	# 	       		buyValue=np.append(buyValue,currentPrice)
	# 	       		if(len(buyValue)>60):
	# 				buyValue=np.delete(buyValue,0)
	#        	if(cciBuy==-1 and rsiBuy==-1 and macBuy==-1):
	# 	       		Sell('ETHBTC',amount)
	# 	       		sellValue=np.append(sellValue,currentPrice)
	# 		       	if(len(sellValue)>60):
	# 	       			sellValue=np.delete(sellValue,0)
	else:
		print "Size Not Large Enough, Waiting For Update"
	time.sleep(1)
	# except:
	# 	print "holl up"
	# else:
	# 	print "gucci"
