from binance.client import Client
import config
import sys
import json
import time
import schedule
import threading

pair='ADAETH'
gmail_user = 'doggo4notification@gmail.com'  
gmail_password = 'doggo4notify'
send_list=['crstradingbot@gmail.com','ryanchenyang@gmail.com','maxpol191999@gmail.com','robxu09@gmail.com']


def sendNotification(subject,mesg):
	try:
		sent_from = gmail_user   
		msg='Subject:'+subject+'\n\n'+mesg.format(subject)
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(gmail_user, send_list, msg)
		server.close()
		print 'Email sent!'
	except:
		print 'Email Send Failure'

def login():
	print "Connecting..."
	try:
		client = Client("as", "fds")
	except:
		sys.exit("Failed to connect") #kills entire interpreter, so if 2 scripts, both die.
	else:
		print "Connected"
	return client
def getKline():
	print "Thread:%s" % threading.current_thread()
	print "Getting Kline"
	try:
		kline=json.dumps(client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_1MINUTE,limit=1))
		print kline
		with open ("/Users/ryan/Desktop/Doggo4/klines.txt", "a") as outkline:				
			outkline.write(kline+"\n")
	except:
		print "holl up kline"
		sendNotification("Fetch Broke","Kline Broke")
	return
def getTicker():
	print "Thread: %s" % threading.current_thread()
	print "Getting Ticker"
	try:
		ticker=json.dumps(client.get_symbol_ticker(symbol=pair))
		print ticker
		with open ("/Users/ryan/Desktop/Doggo4/ticker.txt", "a") as outticker:				
			outticker.write(ticker+"\n")
	except:
		print "holl up ticker"
		sendNotification("Fetch Broke","Ticker Broke")
	return
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
#main
client=login()
schedule.every(1).minute.do(run_threaded,getKline)
schedule.every(1).second.do(getTicker)
while 1:
	schedule.run_pending()
