from binance.client import Client
import config
import sys
import json
import time
pair='ADAETH'
path="/Users/ryan/Desktop/Doggo4/"+pair+".txt"
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
client=login()
while 1:
	try:
		symbol_ticker=json.dumps(client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE,limit=1))
		print symbol_ticker
		#[[1519654380000,"0.08511500","0.08525000","0.08511200","0.08514600","17.33200000",1519654439999,"1.47620423",62,"6.80200000","0.57963530","0"]]
		#symbol_ticker=symbol_ticker.replace("\"","")
		#symbol_ticker=symbol_ticker.replace("\b","")
		#symbol_ticker=symbol_ticker.replace(" ","")
		with open (path, "a") as outfile:				
			outfile.write(symbol_ticker+"\n")
		time.sleep(60)
	except:
		print "holl up"
	else:
		print "gucci"