#TODO
import config
import sys
import json
import numpy as np
import time
from indicators import *
import matplotlib.pyplot as plt
rsi=[0]*172800
rsiStage=1
gain=0
loss=0
rsiReady=False
canStart=False
counter=1
change=ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2]
while 1:
	if(counter<15):
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
            rsi_array.append(rsi(avgg,avgl))
            del rsi_array[0]
	time.sleep(1)
		
		
#initialize list names with correct lengths. sma, upper, rsi etc. fill size and with zeros.
#make each indicator a boolean isReady variable. start as false
#make each indicator a counter for how many times they were updated. when each has reached a certain amount, set true
#when however many/all are set true, can move on to rest of code
#same format as indicators, except make a bool variable for each for whether they were run thru/filled enough times. counter variable

#example
#rsiCounter = 0;
#rsiIsReady = false;
#if(rsiCounter>3456765456) then rsiIsReady = true;
#if(rsiIsReady = true and emaIsReady = true and bollIsReady = true) then canStart



#if(ethbtcprices list length < some number) get ethBtc price, append to list.
#else get ethbtcprice append to list, delete [0], do rest of code



#sma looks same as indicators sma.

#ema initialize first ema as 0. make sure it doesn't overwrite. In this class you can initialize values at top, as long as organized


#rsi
#there are two stages
#first stage
#for first however many (14) amount of ticks, define as gain or loss through if statements, and add up in two variables. gains and losses
#example: first 14 ticks there were 10 gains and 4 losses. all gains added up = gains. all losses added up = losses
#after the 14 ticks do this:
#averagegain variable = gains/14
#averageloss variable = loss/14
#update stage

#after first stage is done, you will do this instead. do not come here on same tick as first stage
#current gains/ current losses code copy pasta from indicators
#avggains and avglosses code copypasta

#both stages feed here
#get rs which is averagegains/averageloss
#append 100-100/(1+rs)
#rsicounter+=1

#boll looks same as boll in indicators


#Continuiously get all data that is needed for bot to start
#(rsi,sma for middle boll, etc)
#feed data to indicators
#Do not let bot start until all data is retreived, and keep updating until bot starts, all arrays must be filled
#Give data to bot
