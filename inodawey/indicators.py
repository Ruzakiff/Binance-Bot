import numpy as np
import time
lower=[0]*172800
upper=[0]*172800
lengthTime=172800

def sma(price,seconds):
	temp=0
	for x in xrange(0,seconds):
		temp=temp+price[x]
	return (temp/seconds)
def ema(price,ema):
	return ((price[0]-ema[0])*.181818)+ema[0]
def rsi(avgg,avgl):
	rs=avgg/avgl
	return 100-(100/(1+rs))
def Upboll(sma,closing):
	upper.insert(0,sma[0]+np.std(closing))
	del upper[lengthTime]
	return upper
def Lowboll(sma,closing):
	lower.insert(0,sma[0]-np.std(closing))
	del lower[lengthTime]
	return lower
def Midboll(sma):
	return sma
def Allboll():
	return True
