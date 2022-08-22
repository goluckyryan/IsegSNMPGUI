#!/usr/bin/python3

import IsegLibrary as iseg
import os
import datetime
import csv
import socket
import sys

#assign a port, to prevent the script run mulitple time
s = socket.socket()
host = socket.gethostname()
port = 4305
s.bind((host,port))

nArg = len(sys.argv)

print ( nArg)

if nArg > 1 :
  IP = sys.argv[1]
else :
  IP = input('Mpod IP address to connect : ')

databaseIP="128.186.111.107"
pushToDB = False

#===================== GUI
import PySimpleGUI as sg

sg.theme('DarkPurple5')

header = ["name", "HV [V]", "Current [mA]"]

mpod = iseg.Mpod(IP)
if mpod.isConnected == False:
  exit()

print("============ GUI start")

chList = mpod.GetChList()
hvList = mpod.GetAllHV()    # get all V
iList = mpod.GetAllCurrent() # get all current
outVList = mpod.GetAllOutputHV()
outIList = mpod.GetAllLC() 
onOffList = mpod.GetAllOnOff()

modChList = iseg.SplitChList(chList)

nMod = len(modChList)
nChannel = len(chList)
updateTime = 60 #sec

fileName = ''

layoutTab = []
for k in range(0, nMod):
  layoutTab.append([])

for k in range(0, nMod):
  baseI = 0
  for kk in range(0, k):
    baseI += len(modChList[kk])
  
  ## i know it is stupid to have this every time, but pysimplegui request a non-used array
  layoutTab[k].append([
            sg.Text("Name", size = 8, justification = "center" ),
            sg.Text("CH", size = 4, justification = "center" ),
            sg.Text("On/Off", size = 6, justification = "center"),
            sg.Text("Set V [V]", size = 8, justification = "center" ),
            sg.Text("Set I [mA]", size = 9, justification = "center" ),
            sg.Text("Out V [V]", size = 8, justification = "center" ),
            sg.Text("Out I [uA]", size = 10, justification = "center" )
                      ])
  
  for j in range(0, len(modChList[k])) :
    i = baseI + j
    layoutTab[k].append(
                  [
                    sg.Input(default_text='', size = 8, justification = "left", key=("n%d" % chList[i])),
                    sg.Text("u"+str(chList[i]), size = 4, justification = "center"  ),
                    sg.Checkbox('', default = onOffList[i], size = 3, enable_events = True, key=("c%d" % chList[i])),
                    sg.Input(default_text=("%.3f" % hvList[i]), size = 8, justification = "right", enable_events=True,  key=("v%d" % chList[i]) ),
                    sg.Input(default_text=("%.3f" % (iList[i]*1000)), size = 9, justification = "right", enable_events=True,  key=("i%d" % chList[i]) ),
                    sg.Input(default_text=("%.3f" % outVList[i]), size = 8, justification = "right", enable_events=True,  key=("a%d" % chList[i]), readonly = True ),
                    sg.Input(default_text=("%.3f" % (outIList[i]*1e6)), size = 10, justification = "right", enable_events=True,  key=("b%d" % chList[i]), readonly = True )
                  ]
                  )

layoutTabGroup = []
layoutTabGroup.append([])
for k in range(0, nMod):
  layoutTabGroup[0].append(sg.Tab("Mod-%0d" % k, layoutTab[k]))

layout = [
          [
            sg.Text("IP :", size = 27, justification = "right"),
            sg.Input(IP, size = 16, justification = "right", readonly = True),
          ],
          [
            sg.Text("Database IP :", size = 27, justification = "right"),
            sg.Input(databaseIP, size = 16, justification = "right", key='-DatabaseIP-', readonly = False),
            sg.Checkbox('Enable', key='-DatabaseEnable-', enable_events=True)
          ],
          [
            sg.Text("refresh period [sec] :", size = 27, justification = "right"),
            sg.Input(updateTime, size = 8, justification = "right", enable_events=True,  key=("-Refresh-")) 
          ]
          ,
          [
            sg.TabGroup(layoutTabGroup)
          ]
        ]
  
layout.append([sg.FileSaveAs('Save As', target = '-Save-', initial_folder='~', file_types = (('csv file','*.csv'),)),
               sg.FileBrowse('Load', target = '-Load-', initial_folder='~', file_types = (('csv file','*.csv'),)),
               sg.Input(default_text=fileName, expand_x = True, justification = "left", readonly = True, enable_events=True, key="-Save-" ),
               sg.Input('', visible = False, enable_events=True, key="-Load-" )
              ])
              
comboList = ["Get Rise Rate [V/s]", "Get Fall Rate [V/s]", "Set Rise Rate [V/s]", "Set Fall Rate [V/s]"]
layout.append([sg.Combo(comboList, default_value = comboList[0], size = 20, enable_events=True, key="-VRateCombo-"),
               sg.Text("Ch:", size = 3),
               sg.Combo(chList, default_value = chList[0], size = 4, enable_events=True, key="-VRateCh-"),  
               sg.Input('', size = 6, justification = "right", enable_events=True, key="-VRate-")
              ])

window = sg.Window('Iseg HV Control & Monitor', layout, finalize = True, keep_on_top = True)

for i in range(0, nChannel):
  window[("v%d" % chList[i])].bind("<Return>", "_Enter")
  window[("i%d" % chList[i])].bind("<Return>", "_Enter")
  window[("v%d" % chList[i])].bind("<KP_Enter>", "_Enter")
  window[("i%d" % chList[i])].bind("<KP_Enter>", "_Enter")

# Event Loop to process "events" and get the "values" of the inputs
while True:
  event, values = window.read(timeout = updateTime * 1000, timeout_key = "_TIMEOUT_") ## this pause for 20 sec and wait for event
  #print(event)
  #print(values)
  #print(datetime.datetime.now())
  
  if event == "-Refresh-" :
    updateTime = int(window[event].get());
  
  if event in (None, 'Exit'):
    break
  
  if event[0:1] == 'c' :
    ID = event[1:]
    mpod.SwitchOnHV(int(ID), int(window[event].get()))
  
  if event == '-Save-' :
    fileName = values["Save As"]
    outfile = open(fileName, "w")
    csv_writer = csv.writer(outfile)
    for i in range(0, nChannel):
      papap = [window[("n%d" % chList[i])].get(), "u"+str(chList[i]), window[("v%d" % chList[i])].get(), window[("i%d" % chList[i])].get()]
      csv_writer.writerow( papap  ) 
    outfile.close();
    
  if event == "-Load-" :
    fileName = window["-Load-"].get()
    window['-Save-'].update(fileName)
    infile = open(fileName, "r")
    csv_reader = csv.reader(infile)
    i = 0
    for row in csv_reader:
      window[("n%d" % chList[i])].update(row[0])
      window[("v%d" % chList[i])].update(row[2]) 
      window[("i%d" % chList[i])].update(row[3])
      mpod.SetHV(chList[i], float(row[2]))
      mpod.SetCurrent(chList[i], float(row[3])/1000)
      i += 1
  
  if event in ["-VRateCombo-", "-VRateCh-", "-VRate-"]:
    item = window["-VRateCombo-"].get()
    ch = window["-VRateCh-"].get()
    val = window["-VRate-"].get()
    if item == comboList[0]:
      window["-VRate-"].update("%.3f" % float(mpod.GetHVRiseRate(int(ch))))
    if item == comboList[1]:
      window["-VRate-"].update("%.3f" % float(mpod.GetHVFallRate(int(ch))))
    if item == comboList[2]:
      mpod.SetHVRiseRate(ch, val)
      window["-VRate-"].update("%.3f" % float(mpod.GetHVRiseRate(int(ch))))
    if item == comboList[3]:
      mpod.SetHVFallRate(ch, val)
      window["-VRate-"].update("%.3f" % float(mpod.GetHVFallRate(int(ch))))      
  
  haha = event.find('_Enter')
  if haha > 0 :
    ID = event[:haha]
    ch = int(ID[1:])    
    if event[0:1] == 'v' :
      mpod.SetHV(ch, float(window[ID].get()))
      window[ID].update("%.3f" % mpod.GetHV(ch))
    if event[0:1] == 'i' :
      mpod.SetCurrent(ch, float(window[ID].get())/1000.)
      window[ID].update("%.3f" % (mpod.GetCurrent(ch)*1000))
  
  if event == "-DatabaseEnable-" :
    pushToDB = window["-DatabaseEnable-"].get()
    window["-DatabaseIP-"].update(disabled=pushToDB)

  if event == "_TIMEOUT_" :
    #hvList = GetAllHV()    # get all V
    #iList = GetAllCurrent() # get all current
    outVList = mpod.GetAllOutputHV()
    outIList = mpod.GetAllLC() 
    
    pushToDB = window["-DatabaseEnable-"].get()
    if pushToDB :
      tempFile = open("temp.dat", "w")
    
    for i in range(0, nChannel):
      #window[("v%d" % chList[i])].update("%.3f" % hvList[i])
      #window[("i%d" % chList[i])].update("%.3f" % (iList[i]*1000))
      window[("a%d" % chList[i])].update("%.3f" % outVList[i])
      window[("b%d" % chList[i])].update("%.3f" % (outIList[i]*1e6))
      #==== To DataBase
      if pushToDB :
        tempFile.write("Voltage,Ch=%d value=%f\n" % (chList[i], outVList[i]))
        tempFile.write("LeakageCurrent,Ch=%d value=%f\n" % (chList[i], outIList[i]*1e6))
    
    if pushToDB:
      tempFile.close()
      os.system("curl -XPOST http://%s:8086/write?db=testing --data-binary @temp.dat" % databaseIP )
      
  
window.close()

