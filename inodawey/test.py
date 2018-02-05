import config
import sys
import json
from binance.client import Client

def login():
	print "Connecting..."
	#print config.client_key
	#print config.client_secret
	try:
		client = Client(config.client_key, config.client_secret)
		#rest_client = BinanceRESTAPI(config.client_key, config.client_secret)
		#ws_client = BinanceWebSocketAPI(config.client_key)
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client

#main
client=login()
print client.get_exchange_info()
rest_client.ping()
