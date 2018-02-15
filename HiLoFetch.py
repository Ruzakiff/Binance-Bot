from binance.client import Client
import config
import sys
import json
import time
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
	#try:
	symbol_ticker=json.dumps(client.get_klines(symbol='ETHBTC', interval=Client.KLINE_INTERVAL_1MINUTE))
	temp=symbol_ticker.split('"')[1::2]
	with open ("/Users/ryan/Desktop/inodawey/HighLow.txt", "a") as outfile:				
		print temp
		outfile.write(" ".join(temp))
		outfile.write("\n\n")
	time.sleep(1)
	#except:
		#print "holl up"
	#else:
		#print "gucci"




#ethbtc_close=temp[3::9]


#ethbtc_low=temp[2::9]




#ethbtc_high=temp[1::9]





	#with open ("/Users/ryan/Desktop/inodawey/HighLow.txt", "a") as outfile:
	#	outfile.write(symbol_ticker+"\n\n aasdfasdf")
 # while True:
	# try:
	# 	symbol_ticker=json.dumps(client.get_symbol_ticker(symbol='ETHBTC'))
	# 	symbol_ticker=symbol_ticker.replace("\"","")
	# 	symbol_ticker=symbol_ticker.replace("\b","")
	# 	symbol_ticker=symbol_ticker.replace(" ","")
	# 	print symbol_ticker
	# 	with open ("/Users/ryan/Desktop/inodawey/HighLow.txt", "a") as outfile:
	# 	outfile.write(symbol_ticker+"\n")
	# 	time.sleep(1)
	# except:
	# 	print "holl up"
	# else:
	# 	print "gucci"
	#last_updated=coin[77:86]
	#print last_updated
	
