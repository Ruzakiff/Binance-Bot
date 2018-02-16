#could be dumb, might just append in fetch. txt is dumb

import time
ethbtc_price=np.array([])
datafile=open("/Users/ryan/Desktop/inodawey/ethbtc_price.txt", "r")
while 1:
    where = datafile.tell()
    line = datafile.readline()
    if not line:
        time.sleep(1)
        datafile.seek(where)
    else:
	ethbtc_price=np.append(ethbtc_price,float(line[21:31]) #np array
    	#ethbtc_price.append(float(line[21:31]))
    	if(len(ethbtc_price)>lengthTime):
    		#del ethbtc_price[0]
		ethbtc_price=np.delete(ethbtc_price,0) #has to be numpy, talib wants numpy
