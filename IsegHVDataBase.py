#!/usr/bin/python3

import IsegLibrary as iseg
import os
import socket
import time

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

#------ database
with open('ISEG_TOKEN.txt', 'r') as f:
   token = f.readline()

org = "FSUFoxLab"
ip = "https://fsunuc.physics.fsu.edu/influx/"
write_client = influxdb_client.InfluxDBClient(url=ip, token=token, org=org)
bucket = "ISEG"
write_api = write_client.write_api(write_options=ASYNCHRONOUS)

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
    
    # tempFile = open("temp.dat", "w")
    points = []
    
    for i in range(0, nChannel):
      # tempFile.write("Voltage,Ch=%d value=%f\n" % (chList[i], outVList[i]))
      # tempFile.write("LeakageCurrent,Ch=%d value=%f\n" % (chList[i], outIList[i]*1e6))
      points.append(Point("Voltage").tag("Ch",int(chList[i])).field("value",float(outVList[i])))
      points.append(Point("LeakageCurrent").tag("Ch",int(chList[i])).field("value",float(outIList[i])))


    # tempFile.close()
    
    write_api.write(bucket=bucket, org=org, record=points)
    # os.system("curl -XPOST http://128.186.111.107:8086/write?db=testing --data-binary @temp.dat")

    time.sleep(updateTime)

