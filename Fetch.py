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
while True:
	try:
		symbol_ticker=json.dumps(client.get_symbol_ticker(symbol='ETHBTC'))
		symbol_ticker=symbol_ticker.replace("\"","")
		symbol_ticker=symbol_ticker.replace("\b","")
		symbol_ticker=symbol_ticker.replace(" ","")
		print symbol_ticker
		with open ("/Users/ryan/Desktop/inodawey/ethbtc_close.txt", "a") as outfile: #change filepath to filepath of data.txt
			outfile.write(symbol_ticker+"\n")
			time.sleep(1)
	except:
		print "holl up"
	else:
		print "gucci"
