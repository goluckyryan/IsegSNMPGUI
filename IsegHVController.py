#!/usr/bin/python3

import IsegLibrary as iseg
import os
import datetime
import csv
import socket

#assign a port, to prevent the script run mulitple time
s = socket.socket()
host = socket.gethostname()
port = 4305
s.bind((host,port))

#===================== GUI
import PySimpleGUI as sg

#gui.theme('DarkAmber')

header = ["name", "HV [V]", "Current [mA]"]

chList = iseg.GetChList()
hvList = iseg.GetAllHV()    # get all V
iList = iseg.GetAllCurrent() # get all current
outVList = iseg.GetAllOutputHV()
outIList = iseg.GetAllLC() 

nChannel = 10 #len(chList)
updateTime = 60 #sec

fileName = ''

layout = [
          [
            sg.Text("refresh period [sec] :", size = 27, justification = "right"),
            sg.Input(updateTime, size = 8, justification = "right", enable_events=True,  key=("-Refresh-")) 
          ],
         [
          sg.Text("Name", size = 8, justification = "center" ),
          sg.Text("CH", size = 4, justification = "center" ),
          sg.Text("On/Off", size = 6, justification = "center"),
          sg.Text("Set V [V]", size = 8, justification = "center" ),
          sg.Text("Set I [mA]", size = 9, justification = "center" ),
          sg.Text("Out V [V]", size = 8, justification = "center" ),
          sg.Text("Out I [uA]", size = 10, justification = "center" )
         ]]

for i in range(0, nChannel):
  layout.append([ sg.Input(default_text='', size = 8, justification = "left", key=("n%d" % chList[i])),
                  sg.Text("u"+str(chList[i]), size = 4, justification = "center"  ),
                  sg.Checkbox('', size = 3, enable_events = True, key=("c%d" % chList[i])),
                  sg.Input(default_text=("%.3f" % hvList[i]), size = 8, justification = "right", enable_events=True,  key=("v%d" % chList[i]) ),
                  sg.Input(default_text=("%.3f" % (iList[i]*1000)), size = 9, justification = "right", enable_events=True,  key=("i%d" % chList[i]) ),
                  sg.Input(default_text=("%.3f" % outVList[i]), size = 8, justification = "right", enable_events=True,  key=("a%d" % chList[i]), readonly = True ),
                  sg.Input(default_text=("%.3f" % (outIList[i]*1e6)), size = 10, justification = "right", enable_events=True,  key=("b%d" % chList[i]), readonly = True ),
                ])

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
    iseg.SwitchOnHV(int(ID), int(window[event].get()))
  
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
      iseg.SetHV(chList[i], float(row[2]))
      iseg.SetCurrent(chList[i], float(row[3])/1000)
      i += 1
  
  if event in ["-VRateCombo-", "-VRateCh-", "-VRate-"]:
    item = window["-VRateCombo-"].get()
    ch = window["-VRateCh-"].get()
    val = window["-VRate-"].get()
    if item == comboList[0]:
      window["-VRate-"].update("%.3f" % float(iseg.GetHVRiseRate(int(ch))))
    if item == comboList[1]:
      window["-VRate-"].update("%.3f" % float(iseg.GetHVFallRate(int(ch))))
    if item == comboList[2]:
      iseg.SetHVRiseRate(ch, val)
      window["-VRate-"].update("%.3f" % float(iseg.GetHVRiseRate(int(ch))))
    if item == comboList[3]:
      iseg.SetHVFallRate(ch, val)
      window["-VRate-"].update("%.3f" % float(iseg.GetHVFallRate(int(ch))))      
  
  haha = event.find('_Enter')
  if haha > 0 :
    ID = event[:haha]
    ch = int(ID[1:])    
    if event[0:1] == 'v' :
      iseg.SetHV(ch, float(window[ID].get()))
      window[ID].update("%.3f" % iseg.GetHV(ch))
    if event[0:1] == 'i' :
      iseg.SetCurrent(ch, float(window[ID].get())/1000.)
      window[ID].update("%.3f" % (iseg.GetCurrent(ch)*1000))
  

  if event == "_TIMEOUT_" :
    #hvList = GetAllHV()    # get all V
    #iList = GetAllCurrent() # get all current
    outVList = iseg.GetAllOutputHV()
    outIList = iseg.GetAllLC() 
    
    tempFile = open("temp.dat", "w")
    
    for i in range(0, nChannel):
      #window[("v%d" % chList[i])].update("%.3f" % hvList[i])
      #window[("i%d" % chList[i])].update("%.3f" % (iList[i]*1000))
      window[("a%d" % chList[i])].update("%.3f" % outVList[i])
      window[("b%d" % chList[i])].update("%.3f" % (outIList[i]*1e6))
      #==== To DataBase
      tempFile.write("Voltage,Ch=%d value=%f\n" % (chList[i], outVList[i]))
      tempFile.write("LeakageCurrent,Ch=%d value=%f\n" % (chList[i], outIList[i]))
    
    tempFile.close()
    
    os.system("curl -XPOST http://128.186.111.107:8086/write?db=testing --data-binary @temp.dat")
      
  
window.close()

