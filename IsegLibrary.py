#!/usr/bin/python3
  
import os
import subprocess

class Mpod:
  def __init__(self, ip):
    self.IP = ip
    #cmd0Str = "-v2c -m +WIENER-CRATE-MIB -c guru 128.186.111.101 "
    self.cmd0Str = "-v2c -Op .12 -m +WIENER-CRATE-MIB -c guru %s " % self.IP
    self.isConnected = False
    print( "testing communication via " + self.IP)
    cmdStr = "snmpwalk " + self.cmd0Str
    try :
      result = str(subprocess.check_output(cmdStr, shell=True))
      print( result )
      self.isConnected = True
    except :
      print("cannot establish communitation via " + self.IP)
    
  def SetIP(self, ip):
    self.__init__(ip)
    
  def SendCmd(self, option,cmd):
    if (self.isConnected == False ) : return 0
    if option == 0 :
      cmdStr = "snmpget " + self.cmd0Str + cmd
    elif option == 1:
      cmdStr = "snmpset " + self.cmd0Str + cmd
    elif option == 2:
      cmdStr = "snmpwalk " + self.cmd0Str + cmd
    else :
      cmdStr = "echo option: 0 - get, 1 - set, 2 - walk"
    #print(cmdStr)
    result = str(subprocess.check_output(cmdStr, shell=True))
    return result.lstrip('b\'').rstrip('\'').rstrip('\n')

  #======== Get settings
  def GetHV(self, ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputVoltage.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-3].strip())

  def GetCurrent(self, ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputCurrent.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-3].strip())

  def GetOutputHV(self,ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputMeasurementSenseVoltage.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-3].strip())

  def GetLI(self, ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputMeasurementCurrent.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-3].strip())

  def IsHVOn(self, ch):
    if (self.isConnected == False ) : return 0
    return self.SendCmd(0, "outputSwitch.u"+str(ch))

  def GetHVRiseRate(self, ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputVoltageRiseRate.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-5].strip())

  def GetHVFallRate(self, ch):
    if (self.isConnected == False ) : return 0
    haha = self.SendCmd(0, "outputVoltageFallRate.u" + str(ch))
    aa = haha.find('Float:')
    return float(haha[aa+6:-5].strip())
    
  #======== Get All channel Setting using snmp walk

  def GetChList(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputName")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputName.'):
      if len(k) > 0 :
        aa = k.find("=")
        k = k[0:aa].strip().lstrip('u')
        kaka.append(int(k))
    return kaka

  def GetAllHV(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputVoltage")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputVoltage'):
      if len(k) > 0 :
        aa = k.find("Float:")
        k = k[aa+6: -3].strip()
        kaka.append(float(k))
    return kaka
    
  def GetAllCurrent(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputCurrent")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputCurrent'):
      if len(k) > 0 :
        aa = k.find("Float:")
        k = k[aa+6: -3].strip()
        kaka.append(float(k))
    return kaka

  def GetAllOutputHV(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputMeasurementSenseVoltage")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputMeasurementSenseVoltage'):
      if len(k) > 0 :
        aa = k.find("Float:")
        k = k[aa+6: -3].strip()
        kaka.append(float(k))
    return kaka
    
  def GetAllLC(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputMeasurementCurrent")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputMeasurementCurrent'):
      if len(k) > 0 :
        aa = k.find("Float:")
        k = k[aa+6: -3].strip()
        kaka.append(float(k))
    return kaka
    
  def GetAllOnOff(self):
    if (self.isConnected == False ) : return [0]
    haha = self.SendCmd(2, "outputSwitch")
    kaka = []
    for k in haha.split('WIENER-CRATE-MIB::outputSwitch'):
      if len(k) > 0 :
        aa = k.find("INTEGER:")
        k = k[aa+12:-2].strip('(').strip(')')
        kaka.append(int(k))
    return kaka

  #======== Set Settings
  def SetHV(self, ch, val):
    if (self.isConnected == False ) : return 0
    try :
      int(ch)
      float(val)
      return self.SendCmd(1, "outputVoltage.u" + str(ch) + " F " + str(val))
    except:
      print("either ch is not int or val is not float")
      
  def SetCurrent(self, ch, val):
    if (self.isConnected == False ) : return 0
    try :
      int(ch)
      float(val)
      return self.SendCmd(1, "outputCurrent.u" + str(ch) + " F " + str(val))
    except:
      print("either ch is not int or val is not float")
      
  def SwitchOnHV(self, ch, onOff):
    if (self.isConnected == False ) : return 0
    try :
      int(ch)
      int(onOff)
      self.SendCmd(1, "outputSwitch.u" + str(ch) + " i " + str(10))
      return self.SendCmd(1, "outputSwitch.u" + str(ch) + " i " + str(onOff))
    except :
      print("either ch or onOff is not int")

  def SetHVRiseRate(self, ch, rate):
    if (self.isConnected == False ) : return 0
    try :
      int(ch)
      int(rate)
      return self.SendCmd(1, "outputVoltageRiseRate.u" + str(ch) + " F " + str(rate))
    except:
      print("either ch is not int or rate is not float")
      
  def SetHVFallRate(self, ch, rate):
    if (self.isConnected == False ) : return 0
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

#mpod = Mpod("128.186.111.101")

#print( mpod.GetOutputHV(0)         )
#print( mpod.GetLI(0)         )
#print( GetHVRiseRate(0) )
#print( GetHVFallRate(0) )
#
#print( SendCmd(1, "outputCurrent.u1 F 0.0005"))

#print( SendCmd(2, "outputCurrent"))

#hvList = GetAllOutputHV()
#print(hvList)

#chList = mpod.GetChList()
#print( SplitChList(chList))
#print( len(SplitChList(chList)))
