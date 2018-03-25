import smtplib
def sendNotification(subject,mesg):
	sent_from = gmail_user   
	msg='Subject:'+subject+'\n\n'+mesg.format(subject)
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.ehlo()
	server.login(gmail_user, gmail_password)
	server.sendmail(gmail_user, to, msg)
	server.close()
	print 'Email sent!'
	print 'Email Send Failure'

gmail_user = 'doggo4notification@gmail.com'  
gmail_password = 'doggo4notify'

sent_from = gmail_user  
#to = ['ryanchenyang@gmail.com', 'robxu09@gmail.com','maxpol191999@gmail.com',"crstradingbot@gmail.com"]
to=['ryanchenyang@gmail.com']  
# subject = 'Buying' #Line that causes trouble
# msg = 'Subject:{}\n\nBought'.format(subject)

# server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# server.ehlo()
# server.login(gmail_user, gmail_password)
# server.sendmail(gmail_user, to, msg)
# server.close()
# print 'Email sent!'

sendNotification("bought","asdfasdf")