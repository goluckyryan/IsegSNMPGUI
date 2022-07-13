#!/usr/bin/python3
  
import os
import subprocess
import datetime
import csv

cmd0Str = "-v 2c -m +WIENER-CRATE-MIB -c guru 128.186.111.101 "

def SendCmd(option,cmd):
  if option == 0 :
    cmdStr = "snmpget " + cmd0Str + cmd
  elif option == 1:
    cmdStr = "snmpset " + cmd0Str + cmd
  elif option == 2:
    cmdStr = "snmpwalk " + cmd0Str + cmd
  else :
    cmdStr = "echo option: 0 - get, 1 - set, 2 - walk"
  #print(cmdStr)
  result = str(subprocess.check_output(cmdStr, shell=True))
  return result.lstrip('b\'').rstrip('\'').rstrip('\n')

#======== Get settings
def GetHV(ch):
  haha = SendCmd(0, "outputVoltage.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-3].strip())

def GetCurrent(ch):
  haha = SendCmd(0, "outputCurrent.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-3].strip())

def GetOutputHV(ch):
  haha = SendCmd(0, "outputMeasurementSenseVoltage.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-3].strip())

def GetLI(ch):
  haha = SendCmd(0, "outputMeasurementCurrent.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-3].strip())

def IsHVOn(ch):
  return SendCmd(0, "outputSwitch.u"+str(ch))

def GetHVRiseRate(ch):
  haha = SendCmd(0, "outputVoltageRiseRate.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-5].strip())

def GetHVFallRate(ch):
  haha = SendCmd(0, "outputVoltageFallRate.u" + str(ch))
  aa = haha.find('Float:')
  return float(haha[aa+6:-5].strip())
  
#======== Get All channel Setting using snmp walk

def GetChList():
  haha = SendCmd(2, "outputName")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputName.'):
    if len(k) > 0 :
      aa = k.find("=")
      k = k[0:aa].strip().lstrip('u')
      kaka.append(int(k))
  return kaka

def GetAllHV():
  haha = SendCmd(2, "outputVoltage")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputVoltage'):
    if len(k) > 0 :
      aa = k.find("Float:")
      k = k[aa+6: -3].strip()
      kaka.append(float(k))
  return kaka
  
def GetAllCurrent():
  haha = SendCmd(2, "outputCurrent")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputCurrent'):
    if len(k) > 0 :
      aa = k.find("Float:")
      k = k[aa+6: -3].strip()
      kaka.append(float(k))
  return kaka

def GetAllOutputHV():
  haha = SendCmd(2, "outputMeasurementSenseVoltage")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputMeasurementSenseVoltage'):
    if len(k) > 0 :
      aa = k.find("Float:")
      k = k[aa+6: -3].strip()
      kaka.append(float(k))
  return kaka
  
def GetAllLC():
  haha = SendCmd(2, "outputMeasurementCurrent")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputMeasurementCurrent'):
    if len(k) > 0 :
      aa = k.find("Float:")
      k = k[aa+6: -3].strip()
      kaka.append(float(k))
  return kaka

#======== Set Settings
def SetHV(ch, val):
  return SendCmd(1, "outputVoltage.u" + str(ch) + " F " + str(val))

def SetCurrent(ch, val):
  return SendCmd(1, "outputCurrent.u" + str(ch) + " F " + str(val))

def SwitchOnHV(ch, onOff):
  return SendCmd(1, "outputSwitch.u" + str(ch) + " i " + str(onOff))

def SetHVRiseRate(ch, rate):
  return SendCmd(1, "outputVoltageRiseRate.u" + str(ch) + " F " + str(rate))

def SetHVFallRate(ch, rate):
  return SendCmd(1, "outputVoltageFallRate.u" + str(ch) + " F " + str(rate))

#===================== SandBox

#print( GetOutputHV(0)         )
#print( GetLI(0)         )
#print( GetHVRiseRate(0) )
#print( GetHVFallRate(0) )
#
#print( SendCmd(1, "outputCurrent.u1 F 0.0005"))

#print( SendCmd(2, "outputCurrent"))

#hvList = GetAllOutputHV()
#print(hvList)

#===================== GUI
import PySimpleGUI as sg

#gui.theme('DarkAmber')

header = ["name", "HV [V]", "Current [mA]"]

chList = GetChList()
hvList = GetAllHV()    # get all V
iList = GetAllCurrent() # get all current
outVList = GetAllOutputHV()
outIList = GetAllLC() 
nChannel = len(chList)

updateTime = 5 #sec

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

window = sg.Window('Iseg HV Control', layout, finalize = True, keep_on_top = True)

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
    SwitchOnHV(int(ID), int(window[event].get()))
  
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
      SetHV(chList[i], float(row[2]))
      SetCurrent(chList[i], float(row[3])/1000)
      i += 1
  
  haha = event.find('_Enter')
  if haha > 0 :
    ID = event[:haha]
    ch = int(ID[1:])    
    if event[0:1] == 'v' :
      SetHV(ch, float(window[ID].get()))
      window[ID].update("%.3f" % GetHV(ch))
    if event[0:1] == 'i' :
      SetCurrent(ch, float(window[ID].get())/1000.)
      window[ID].update("%.3f" % (GetCurrent(ch)*1000))
  

  if event == "_TIMEOUT_" :
    #hvList = GetAllHV()    # get all V
    #iList = GetAllCurrent() # get all current
    outVList = GetAllOutputHV()
    outIList = GetAllLC() 
    
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

