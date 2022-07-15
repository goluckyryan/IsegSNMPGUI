#!/usr/bin/python3
  
import os
import subprocess

#cmd0Str = "-v2c -m +WIENER-CRATE-MIB -c guru 128.186.111.101 "
cmd0Str = "-v2c -Op .12 -m +WIENER-CRATE-MIB -c guru 128.186.111.101 "

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
  
def GetAllOnOff():
  haha = SendCmd(2, "outputSwitch")
  kaka = []
  for k in haha.split('WIENER-CRATE-MIB::outputSwitch'):
    if len(k) > 0 :
      aa = k.find("INTEGER:")
      k = k[aa+12:-2].strip('(').strip(')')
      kaka.append(int(k))
  return kaka

#======== Set Settings
def SetHV(ch, val):
  try :
    int(ch)
    float(val)
    return SendCmd(1, "outputVoltage.u" + str(ch) + " F " + str(val))
  except:
    print("either ch is not int or val is not float")
    
def SetCurrent(ch, val):
  try :
    int(ch)
    float(val)
    return SendCmd(1, "outputCurrent.u" + str(ch) + " F " + str(val))
  except:
    print("either ch is not int or val is not float")
    
def SwitchOnHV(ch, onOff):
  try :
    int(ch)
    int(onOff)
    SendCmd(1, "outputSwitch.u" + str(ch) + " i " + str(10))
    return SendCmd(1, "outputSwitch.u" + str(ch) + " i " + str(onOff))
  except :
    print("either ch or onOff is not int")

def SetHVRiseRate(ch, rate):
  try :
    int(ch)
    int(rate)
    return SendCmd(1, "outputVoltageRiseRate.u" + str(ch) + " F " + str(rate))
  except:
    print("either ch is not int or rate is not float")
    
def SetHVFallRate(ch, rate):
  try :
    int(ch)
    int(rate)
    return SendCmd(1, "outputVoltageFallRate.u" + str(ch) + " F " + str(rate))
  except:
    print("either ch is not int or rate is not float")

#===================== Auxliary function

def SplitChList(chList):
  sep = list()
  for i in range(0, len(chList)):
    if i == 0 :
      sep.append(i)

    if (i < len(chList)-1) and (chList[i+1] - chList[i]) > 1 :
      sep.append(i+1)
    
    if i == len(chList)-1:
      sep.append(i+1)
  newChList = list()
  for i in range(0, len(sep)-1):
    newChList.append( chList[sep[i]:sep[i+1]] )
  return newChList    
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

#chList = GetChList()
#print( SplitChList(chList))
#print( len(SplitChList(chList)))
