#!/usr/bin/python3

import IsegLibrary as iseg
import os
import datetime
import csv
import socket
import sys
import time

# import influxdb_client
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

# #------ database
# with open('ISEG_TOKEN.txt', 'r') as f:
#    token = f.readline().replace('\n', '')

# org = "FSUFoxLab"
# ip = "https://fsunuc.physics.fsu.edu/influx/"
# write_client = influxdb_client.InfluxDBClient(url=ip, token=token, org=org)
# bucket = "ISEG"
# write_api = write_client.write_api(write_options=ASYNCHRONOUS)

#assign a port, to prevent the script run mulitple time
s = socket.socket()
host = socket.gethostname()
port = 4305
s.bind((host,port))

nArg = len(sys.argv)

if nArg > 1 :
  IP = sys.argv[1]
else :
  IP = input('Mpod IP address to connect : ')

#Sergio MPOD 128.186.111.101
#ANASEN MPOD 128.186.111.208

databaseIP="128.186.111.108"
pushToDB = False

#===================== GUI

mpod = iseg.Mpod(IP)
if mpod.isConnected == False:
  exit()

chList = mpod.GetChList()
hvList = mpod.GetAllHV()    # get all V
iList = mpod.GetAllCurrent() # get all current
outVList = mpod.GetAllOutputHV()
outIList = mpod.GetAllLC() 
onOffList = mpod.GetAllOnOff()

modChList = iseg.SplitChList(chList)

nMod = len(modChList)
nChPerMod = []
for k in range(0, nMod):
  nChPerMod.append(len(modChList[k]))
nChannel = len(chList)
updateTime = 1 #sec

print(onOffList)

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox, QLineEdit, QLabel, QVBoxLayout, QWidget, QTabWidget, QGridLayout
from PyQt6.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal
from functools import partial

ColStrList = ["Name", "Ch", 'On/Off', "Set V [V]", "Set I [mA]", "Out V [V]", "Out I [uA]"]

# class TimerThread(QThread):
#   timeout = pyqtSignal()
#   waitTime = int(1)

#   def SetTime(self, time_in_sec):
#     self.waitTime = time_in_sec

#   def run(self):
#     timer = QTimer(self)
#     timer.setInterval(self.waitTime)  # 1 second
#     timer.timeout.connect(self.timeout.emit)
#     timer.start()


class MyWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    self.setWindowTitle("Iseg Controller (" +  str(IP) + ")")
    self.setGeometry(100, 100, 500, 200)
  
    widget = QWidget()
    layout = QVBoxLayout()
    widget.setLayout(layout)
    self.setCentralWidget(widget)

    self.txtName = [[QLineEdit() for _ in range(rows)] for rows in nChPerMod]
    self.txtV = [[QLineEdit() for _ in range(rows)] for rows in nChPerMod]
    self.txtI = [[QLineEdit() for _ in range(rows)] for rows in nChPerMod]
    self.txtVOut = [[QLineEdit() for _ in range(rows)] for rows in nChPerMod]
    self.txtIOut = [[QLineEdit() for _ in range(rows)] for rows in nChPerMod]
    self.chkON = [[QCheckBox() for _ in range(rows)] for rows in nChPerMod]

    # timer = TimerThread()
    # timer.timeout.connect(self.on_timeout)
    # timer.start()

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.updateTimer)
    self.time = 0
    self.timer.start(updateTime*1000)

    #=========== set tab
    self.tabWidget = QTabWidget(self)
    layout.addWidget(self.tabWidget)

    for k in range(0, nMod):
      tab = QWidget(self)
      layout_tab = QGridLayout()
      layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
      tab.setLayout(layout_tab)

      for index, lb in enumerate(ColStrList):
        qlb = QLabel(lb, tab)
        layout_tab.addWidget(qlb, 0, index)

      for i, a in enumerate(modChList[k]) :
        for j, lb in enumerate(ColStrList) : 
          #------------ name
          if j == 0:
            layout_tab.addWidget(self.txtName[k][i], 1+i, j)
          
          #------------ Ch
          if j == 1:
            qlb = QLabel(str(a - 100*k), tab)
            layout_tab.addWidget(qlb, 1+i, j, alignment=Qt.AlignmentFlag.AlignCenter)
          
          #------------ On/Off
          if j == 2:
            if onOffList[sum(nChPerMod[:k]) + i] == 0 :
              self.chkON[k][i].setChecked(False)
            if onOffList[sum(nChPerMod[:k]) + i] == 1 :
              self.chkON[k][i].setChecked(True)
            if onOffList[sum(nChPerMod[:k]) + i] == 3 :
              self.chkON[k][i].setChecked(False)
              self.chkON[k][i].setStyleSheet("background-color: red;")
            
            layout_tab.addWidget(self.chkON[k][i], 1+i, j, alignment=Qt.AlignmentFlag.AlignCenter)
          
            self.chkON[k][i].clicked.connect(partial(self.SetOnOff, k, i))
          #------------ V set
          if j == 3:
            self.txtV[k][i].setText(str(hvList[sum(nChPerMod[:k]) + i]))
            self.txtV[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtV[k][i], 1+i, j)

            self.txtV[k][i].returnPressed.connect(partial(self.SetHV, k, i) )
          #------------ I set
          if j == 4:
            self.txtI[k][i].setText("{:.2f}".format(iList[sum(nChPerMod[:k]) + i]*1000))
            self.txtI[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtI[k][i], 1+i, j)
          
            self.txtI[k][i].returnPressed.connect(partial(self.SetI, k, i) )
          #------------ V out
          if j == 5:
            self.txtVOut[k][i].setText("{:.2f}".format(outVList[sum(nChPerMod[:k]) + i]))
            self.txtVOut[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtVOut[k][i], 1+i, j)
            self.txtVOut[k][i].setReadOnly(True)
            self.txtVOut[k][i].setStyleSheet("background-color: lightgrey;")
          
          #------------ I out
          if j == 6:
            self.txtIOut[k][i].setText("{:.2f}".format(outIList[sum(nChPerMod[:k]) + i]*1e6))
            self.txtIOut[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtIOut[k][i], 1+i, j)
            self.txtIOut[k][i].setReadOnly(True)
            self.txtIOut[k][i].setStyleSheet("background-color: lightgrey;")

      self.tabWidget.addTab(tab, "Mod-" + str(k))

  def SetHV(self, mod, ch):
    value = float(self.txtV[mod][ch].text())
    print("mod : " +  str(mod) + ", ch : " + str(ch) + " | " +  str(value))
    mpod.SetHV( mod*100 + ch, value)

  def SetI(self, mod, ch):
    value = float(self.txtI[mod][ch].text())
    print("mod : " +  str(mod) + ", ch : " + str(ch) + " | " +  str(value))
    mpod.SetCurrent( mod*100 + ch, value/1000.)

  def SetOnOff(self, mod, ch):
    state = self.chkON[mod][ch].checkState()
    print("mod : " +  str(mod) + ", ch : " + str(ch) + " | " +  str(state))
    if state == Qt.Checked :
      mpod.SwitchOnHV( mod*100 + ch, True)
    else:
      mpod.SwitchOnHV( mod*100 + ch, False)

  def on_timeout(self):
    print("Timer timed out!")

  def updateTimer(self):
    self.time += 1
    print(f'Time: {self.time}')

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MyWindow()
  window.show()
  sys.exit(app.exec())