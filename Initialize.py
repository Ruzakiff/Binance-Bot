#TODO
import config
import sys
import json
import numpy as np
import time
from indicators import *
rsi_array=[0]*172800
firstGain=0
firstLoss=0
rsiReady=False
canStart=False
botIsOff=True
avgGain=0
avgLoss=0 
time=1
def botOn():
	botIsOff=False
def botOff():
	botIsOff=True
while (botIsOff):
	change=ethbtc_price[len(ethbtc_price)-1]-ethbtc_price[len(ethbtc_price)-2]
	currentGain=0
	currentLoss=0
	if(change>0):
		currentGain=change
		currentLoss=0
	if(change<0):
		currentGain=0
		currentLoss=abs(change)
      	if(change==0):
		currentGain=0
		currentLoss=0
	if(time<=14):
		if(change>0):
			firstGain=firstGain+change
		if(change<0):
                	firstLoss=firstLoss+abs(change)
        if(time==15):
		firstGain=firstGain/14
		firstLoss=firstLoss/14
		avgGain=(firstGain*13+currentGain)/14
		avgLoss=(firstLoss*13+currentLoss)/14
		rsi_array.append(100-(100/1+(avgGain/avgLoss))
        if(time>14):
		avgGain=(avgGain*13+currentGain)/14
		avgLoss=(avgLoss*13+currentLoss)/14
		rsi_array.append(100-(100/1+(avgGain/avgLoss))
		if(rsi_array>172800):
			rsiReady=True
            		del rsi_array[0]
	if(rsiReady):
		canStart=True
	time.sleep(1)
	time=time+1
		
		
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
