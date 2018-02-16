from binance.client import Client
import numpy as np
import config
import sys
import json
import time
ethbtc_close=np.array([])
ethbtc_high=np.array([])
ethbtc_low=np.array([])
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
while 1:
	try:
		symbol_ticker=json.dumps(client.get_klines(symbol='ETHBTC', interval=Client.KLINE_INTERVAL_1MINUTE))
		temp=symbol_ticker.split('"')[1::2]
		ethbtc_close=np.append(ethbtc_close,temp[3::9])
		ethbtc_low=np.append(ethbtc_low,temp[2::9])
		ethbtc_high=np.append(ethbtc_high,temp[1::9])
		with open ("/Users/ryan/Desktop/inodawey/HighLow.txt", "a") as outfile:				
			outfile.write(ethbtc_high+"\n")
			outfile.write(ethbtc_low+"\n")
			outfile.write(ethbtc_close+"\n")
		while(len(ethbtc_close)>=1500):
			np.delete(ethbtc_close,0)
		while(len(ethbtc_low)>=1500):
			np.delete(ethbtc_low,0)
		while(len(ethbtc_high)>=1500):
			np.delete(ethbtc_high,0)
		time.sleep(60)
	except:
		print "holl up"
	else:
		print "gucci"

#ethbtc_close=temp[3::9]
#ethbtc_low=temp[2::9]
#ethbtc_high=temp[1::9]
