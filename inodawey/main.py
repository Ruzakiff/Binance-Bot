#imports
from binance.client import Client
import config
import sys
import json
import numpy as np
import time
from indicators import *
import matplotlib.pyplot as plt
#initializations
lengthTime=172800 #2day
ethbtc_ticker_array=[0]*lengthTime #1 day, might be 86400-1, can also replace with numpy array

sma_array=[0]*lengthTime
ema_array=[0]*lengthTime
rsi_array=[0]*lengthTime
counter=1
avgg=0
avgl=0
gain=0
loss=0
x=np.arange(lengthTime)
def login():
	print "Connecting..."
	#print config.client_key
	#print config.client_secret
	try:
		client = Client(config.client_key, config.client_secret)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client

#main
client=login();
datafile=open("/Users/ryan/Desktop/inodawey/data.txt", "r")
while 1:
    where = datafile.tell()
    line = datafile.readline()
    if not line:
        time.sleep(1)
        datafile.seek(where)
    else:
    	ethbtc_ticker_array.append(float(line[21:31]))
        del ethbtc_ticker_array[0]
        #get eth first
        change=ethbtc_ticker_array[lengthTime-1]-ethbtc_ticker_array[lengthTime-2]
        #rsi
        if(counter<=15):
            if(change>0):
                gain=gain+change
            if(change<0):
                loss=loss+abs(change)
        if(counter==15):
            gain=gain/14
            loss=loss/14
            if(change>0):
                avgg=(gain*13+change)/14
                avgl=(gain*13+0)/14
            if(change<0):
                avgg=(gain*13+0)/14
                avgl=(gain*13+abs(change))/14
            if(change==0):
                avgg=(gain*13+0)/14
                avgl=(gain*13+0)/14
        if(counter>15):
            if(change>0):
                avgg=(avgg*13+change)/14
                avgl=(avgl*13+0)/14
            if(change<0):
                avgg=(avgg*13+0)/14
                avgl=(avgl*13+abs(change))/14
            if(change==0):
                avgg=(avgg*13+0)/14
                avgl=(avgl*13+0)/14
            print rsi(avgg,avgl)
            rsi_array.append(rsi(avgg,avgl))
            del rsi_array[0]
        ema_array.append(ema(ethbtc_ticker_array,ema_array))
        del ema_array[0]
        #print ema_array
        sma_array.append(sma(ethbtc_ticker_array,counter))
        del sma_array[0]
        counter=counter+1 #temp
        upper=Upboll(sma_array,ethbtc_ticker_array)
        lower=Upboll(sma_array,ethbtc_ticker_array)
        middle=Midboll(sma_array)
        #print upper
        #print lower
        #t1=np.polyfit(x,sma_array,4)
        #t2=np.polyfit(x,upper,4)
        #t3=np.polyfit(x,lower,10)
        #print t3
        #plot(t1)
        plt.plot(x,lower,color='green')
        plt.plot(x,upper,color='blue')
        
        #plot(t2)
        #plot(t3)
        #plt.xlim([0,100])
        #plt.ylim([0.10000000000001, 0.11])
        plt.show()

        #plt.plot(sma_array)
        #plt.plot(ema_array)
       #print plt.get_xlim
        #plt.show()
    	#print ethbtc_ticker_array
        #print line # already has newline
#print client
#candles = client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_30MINUTE)
#price=client.get_order_book(symbol='BNBBTC')
#exchange=client.get_exchange_info()
#print price
#print exchange
#address = client.get_deposit_address(asset='BTC')
#eth_withdraws = client.get_withdraw_history(asset='ETH')
#print address

#make new script to keep fetching and writting, and this will read the file