#!/usr/bin/python3

import IsegLibrary as iseg
import os
import socket
import time

#assign a port, to prevent the script run mulitple time
s = socket.socket()
host = socket.gethostname()
port = 4305
s.bind((host,port))


chList = iseg.GetChList()
nChannel = len(chList)

updateTime = 2 #sec

# Event Loop to process "events" and get the "values" of the inputs
while True:
    outVList = iseg.GetAllOutputHV()
    outIList = iseg.GetAllLC() 
    
    tempFile = open("temp.dat", "w")
    
    for i in range(0, nChannel):
      tempFile.write("Voltage,Ch=%d value=%f\n" % (chList[i], outVList[i]))
      tempFile.write("LeakageCurrent,Ch=%d value=%f\n" % (chList[i], outIList[i]*1e6))
    
    tempFile.close()
    
    os.system("curl -XPOST http://128.186.111.107:8086/write?db=testing --data-binary @temp.dat")

    time.sleep(updateTime)

