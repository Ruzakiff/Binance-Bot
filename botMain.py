from binance.client import Client
import config
import sys
import json
import numpy as np
import time
from indicators import *
import matplotlib.pyplot as plt

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
