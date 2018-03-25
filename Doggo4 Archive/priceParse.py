#could be dumb, might just append in fetch. txt is dumb
import time
import numpy as np
ethbtc_price=np.array([])
datafile=open("/Users/ryan/Desktop/Doggo4/ethbtc_price.txt", "r")
while True:
    where=datafile.tell()
    line=datafile.readline()
    if not line:
        time.sleep(1)
        datafile.seek(where)
    else:
        #print float(line[21:31])
        ethbtc_price=np.append(ethbtc_price,float(line[21:31]))
        if(len(ethbtc_price)>172800):
            ethbtc_price=np.delete(ethbtc_price,0)