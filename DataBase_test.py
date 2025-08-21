#!/usr/bin/python3

import IsegLibrary as iseg
import os
import socket
import time

dataBaseAddress = "192.168.1.193"

IP = "192.168.2.55"
mpod = iseg.Mpod(IP)

chList = mpod.GetChList()
outVList = mpod.GetAllOutputHV()
outIList = mpod.GetAllLC() 

# print(chList)

# print(outIList)

with open("output.txt", "w") as f:
    for i, ch in enumerate(chList):
        det = ch % 100
        module = ch // 100
        line = f"HV,Det={det},Module={module} value={outVList[i]:.3f}\n"
        f.write(line)
        line = f"LC,Det={det},Module={module} value={outIList[i]*1e6:.3f}\n"
        f.write(line)
    
DB_BashCommand_Mac='curl -sS -i -XPOST "http://%s:8086/write?db=testing" --data-binary @output.txt --speed-time 5 --speed-limit 1000' % dataBaseAddress

os.system(DB_BashCommand_Mac)