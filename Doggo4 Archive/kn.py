import numpy as np
count=np.zeros((27,), dtype=int)
print len(count)
content=open("/Users/ryan/Desktop/no.txt",'r').read()
content=content.split("\n")
number=0
while(number!=81):
	for lines in content:
		if(lines[number]=="A"):
			count[0]=count[0]+1
		if(lines[number]=="B"):
			count[1]=count[1]+1
		if(lines[number]=="C"):
			count[2]=count[2]+1
		if(lines[number]=="D"):
			count[3]=count[3]+1
		if(lines[number]=="E"):
			count[4]=count[4]+1
		if(lines[number]=="F"):
			count[5]=count[5]+1
		if(lines[number]=="G"):
			count[6]=count[6]+1
		if(lines[number]=="H"):
			count[7]=count[7]+1
		if(lines[number]=="I"):
			count[8]=count[8]+1		
		if(lines[number]=="J"):
			count[9]=count[9]+1
		if(lines[number]=="K"):
			count[10]=count[10]+1
		if(lines[number]=="L"):
			count[11]=count[11]+1
		if(lines[number]=="M"):
			count[12]=count[12]+1
		if(lines[number]=="N"):
			count[13]=count[13]+1
		if(lines[number]=="O"):
			count[14]=count[14]+1
		if(lines[number]=="P"):
			count[15]=count[15]+1
		if(lines[number]=="Q"):
			count[16]=count[16]+1
		if(lines[number]=="R"):
			count[17]=count[17]+1
		if(lines[number]=="S"):
			count[18]=count[18]+1
		if(lines[number]=="T"):
			count[19]=count[19]+1
		if(lines[number]=="U"):
			count[20]=count[20]+1
		if(lines[number]=="V"):
			count[21]=count[21]+1
		if(lines[number]=="W"):
			count[22]=count[22]+1
		if(lines[number]=="X"):
			count[23]=count[23]+1
		if(lines[number]=="Y"):
			count[24]=count[24]+1
		if(lines[number]=="Z"):
			count[25]=count[25]+1
		if(lines[number]=="9"):
			count[26]=count[26]+1
	print count
	
	print "\n"
	count=np.zeros((27,), dtype=int)
	number=number+1


	#print lines[number]
#print len(content)