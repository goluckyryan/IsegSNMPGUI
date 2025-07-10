#!/usr/bin/python3

import IsegLibrary as iseg
import os
import datetime
import csv
import socket
import sys
import time

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

#------ database
try:
  with open('ISEG_TOKEN.txt', 'r') as f:
    token = f.readline()
except:
    print("Error: ISEG_TOKEN.txt file not found.")
    token = None  # Or assign a default value if needed

org = ""
databaseIP="192.168.1.193"
write_client = influxdb_client.InfluxDBClient(url=databaseIP, token=token, org=org)
bucket = ""
# write_api = write_client.write_api(write_options=ASYNCHRONOUS)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

nArg = len(sys.argv)

if nArg > 1 :
  IP = sys.argv[1]
else :
  IP = input('Mpod IP address to connect : ')

#Sergio MPOD 128.186.111.101
#ANASEN MPOD 128.186.111.208

pushToDB = False


#============== assign a port, to prevent the script run mulitple time
s = socket.socket()
host = socket.gethostname()
port = 4300 + int(IP[-2:])
print("using port " + str(port))
s.bind((host,port))

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
modIndex = []
nChPerMod = []
for k in range(0, nMod):
  modIndex.append(int(modChList[k][0]/100))
  nChPerMod.append(len(modChList[k]))
nChannel = len(chList)
updateTime = 3 #sec

# print("######")
# print(iList)
# print(onOffList)

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QCheckBox, QLineEdit, QLabel, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QMessageBox, QFileDialog, QProgressBar
from PyQt6.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal
from functools import partial

ColStrList = ["Name", "Ch", 'On/Off', "Set V [V]", "Set I [uA]", "Out V [V]", "Out I [uA]"]

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

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.updateTimer)
    # self.time = 0
    self.timer.start(updateTime*1000)

    #=========== database and refresh time
    gLayout = QGridLayout()
    layout.addLayout(gLayout)

    lbIP = QLabel("Database IP : ", self)
    lbIP.setAlignment(Qt.AlignmentFlag.AlignRight)
    gLayout.addWidget(lbIP, 0, 0)
    
    self.txtIP = QLineEdit(self)
    self.txtIP.setText(databaseIP)
    self.txtIP.textChanged.connect(partial(self.TextChange, self.txtIP))
    self.txtIP.returnPressed.connect(partial(self.UnSetTextColor, self.txtIP))
    gLayout.addWidget(self.txtIP, 0, 1)

    self.chkDB = QCheckBox("Enable", self)
    gLayout.addWidget(self.chkDB, 0, 2)
    # if token == None:
    #   self.txtIP.setEnabled(False)
    #   self.chkDB.setEnabled(False)

    lb1 = QLabel("Refresh period [sec] :", self)
    lb1.setAlignment(Qt.AlignmentFlag.AlignRight)
    gLayout.addWidget(lb1, 1, 0)
    
    self.txtRefresh = QLineEdit(self)
    self.txtRefresh.setText(str(updateTime))
    self.txtRefresh.textChanged.connect(partial(self.TextChange, self.txtRefresh))
    self.txtRefresh.returnPressed.connect(self.SetTimer)
    self.txtRefresh.returnPressed.connect(partial(self.UnSetTextColor, self.txtRefresh))
    gLayout.addWidget(self.txtRefresh, 1, 1)

    self.AllChkOn = QPushButton("Switch all channels On.")
    gLayout.addWidget(self.AllChkOn, 2, 1)
    self.AllChkOn.clicked.connect(partial(self.SwitchOnAllCh))

    self.AllChkOff = QPushButton("Switch all channels off.")
    gLayout.addWidget(self.AllChkOff, 3, 1)
    self.AllChkOff.clicked.connect(partial(self.SwitchOffAllCh))

    #=========== set tab
    self.tabWidget = QTabWidget(self)
    layout.addWidget(self.tabWidget)

    for k in range(0, nMod): # k is running from 0, 1, 2, ....
      tab = QWidget(self)
      layout_tab = QGridLayout()
      layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
      tab.setLayout(layout_tab)

      for index, lb in enumerate(ColStrList):
        qlb = QLabel(lb, tab)
        layout_tab.addWidget(qlb, 0, index)

      initRow = 1
      for i, a in enumerate(modChList[k]) : # a is the channel ID
        for j, lb in enumerate(ColStrList) : 
          #------------ name
          if j == 0:
            layout_tab.addWidget(self.txtName[k][i], initRow + i, j)
          
          #------------ Ch
          if j == 1:
            # print(f"{a}, {k}, {a-100*k}")
            qlb = QLabel(str(a), tab)
            layout_tab.addWidget(qlb, initRow + i, j, alignment=Qt.AlignmentFlag.AlignCenter)
          
          #------------ On/Off
          if j == 2:
            if onOffList[sum(nChPerMod[:k]) + i] == 0 :
              self.chkON[k][i].setChecked(False)
            if onOffList[sum(nChPerMod[:k]) + i] == 1 :
              self.chkON[k][i].setChecked(True)
            if onOffList[sum(nChPerMod[:k]) + i] == 3 :
              self.chkON[k][i].setChecked(False)
              self.chkON[k][i].setStyleSheet("background-color: red;")
            
            layout_tab.addWidget(self.chkON[k][i], initRow + i, j, alignment=Qt.AlignmentFlag.AlignCenter)
          
            self.chkON[k][i].clicked.connect(partial(self.SetOnOff, k, i))
          #------------ V set
          if j == 3:
            self.txtV[k][i].setText(str(hvList[sum(nChPerMod[:k]) + i]))
            self.txtV[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtV[k][i], initRow + i, j)

            self.txtV[k][i].returnPressed.connect(partial(self.SetHV, k, i) )
            self.txtV[k][i].returnPressed.connect(partial(self.UnSetTextColor, self.txtV[k][i]))
            self.txtV[k][i].textChanged.connect(partial(self.TextChange, self.txtV[k][i]))
            
          #------------ I set
          if j == 4:
            self.txtI[k][i].setText("{:.2f}".format(iList[sum(nChPerMod[:k]) + i]*1e6))
            self.txtI[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtI[k][i], initRow + i, j)
          
            self.txtI[k][i].returnPressed.connect(partial(self.SetI, k, i) )
            self.txtI[k][i].returnPressed.connect(partial(self.UnSetTextColor, self.txtI[k][i]))
            self.txtI[k][i].textChanged.connect(partial(self.TextChange, self.txtI[k][i]))

          #------------ V out
          if j == 5:
            self.txtVOut[k][i].setText("{:.2f}".format(outVList[sum(nChPerMod[:k]) + i]))
            self.txtVOut[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtVOut[k][i], initRow + i, j)
            self.txtVOut[k][i].setReadOnly(True)
            self.txtVOut[k][i].setStyleSheet("background-color: lightgrey;")
          
          #------------ I out
          if j == 6:
            self.txtIOut[k][i].setText("{:.2f}".format(outIList[sum(nChPerMod[:k]) + i]*1e6))
            self.txtIOut[k][i].setAlignment(Qt.AlignmentFlag.AlignRight)
            layout_tab.addWidget(self.txtIOut[k][i], initRow + i, j)
            self.txtIOut[k][i].setReadOnly(True)
            self.txtIOut[k][i].setStyleSheet("background-color: lightgrey;")

      self.tabWidget.addTab(tab, "Mod-" + str(modIndex[k]))
    
    #============= Save setting
    sLayout = QGridLayout()
    layout.addLayout(sLayout)

    bLoad = QPushButton("Load", self)
    bLoad.clicked.connect(self.LoadSetting)
    sLayout.addWidget(bLoad, 0, 0)

    self.txtFile = QLineEdit(self)
    sLayout.addWidget(self.txtFile, 0, 1)

    bSave = QPushButton("Save", self)
    bSave.clicked.connect(self.SaveSetting)
    sLayout.addWidget(bSave, 0, 3)
  
    #============= General Setting #TODO

  ######################################################### slots
  def SaveSetting(self):
    fileName = self.txtFile.text()
    if fileName == "" :
      return
    outfile = open(fileName, "w")
    csv_writer = csv.writer(outfile)
    for k in range(0, nMod):
      for i, a in enumerate(modChList[k]) :
        papap = [self.txtName[k][i].text(), "u"+str(modChList[k][i]), self.txtV[k][i].text(),self.txtI[k][i].text()]
        csv_writer.writerow( papap  ) 
    outfile.close()
    self.txtFile.setText( fileName + " (Saved)")
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setText("Setting saved to " +  fileName + "as a csv file.")
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()

  def LoadSetting(self):
    file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;All Files (*)")
        
    if file_path:
      infile = open(file_path, "r")
      csv_reader = csv.reader(infile)
      row_count = sum(1 for row in csv_reader)
      infile.seek(0)
      count = 0
      for row in csv_reader:
        ch = row[1]
        if ch.startswith('u') and ch[1:].isdigit():
          chID = int(ch[1:]) % 100
          modID = int(int(ch[1:]) / 100) 
          # print(str(modID) + "," + str(chID))

          self.txtName[modID][chID].setText(row[0])
          self.txtName[modID][chID].setStyleSheet("")
          self.txtV[modID][chID].setText(row[2])
          self.txtV[modID][chID].setStyleSheet("")
          self.txtI[modID][chID].setText(row[3])
          self.txtI[modID][chID].setStyleSheet("")

          # print("Setting " + row[1] )
          mpod.SetHV(int(ch[1:]), float(row[2]))
          time.sleep(0.01)
          mpod.SetCurrent(int(ch[1:]), float(row[3])/1000)
          time.sleep(0.01)
          count = count+1
          self.txtFile.setText("Loading Setting, %d/%d ." % (count, row_count))
          self.repaint()

      self.txtFile.setText(file_path + " (Loaded)")

  def UnSetTextColor(self, qLineEdit : QLineEdit):
    qLineEdit.setStyleSheet("")

  def TextChange(self, qLineEdit : QLineEdit):
    qLineEdit.setStyleSheet("color : darkgreen;")

  def SetTimer(self):
    sec = float(self.txtRefresh.text())
    self.timer.stop()
    self.timer.start(int(sec * 1000))

  def SetHV(self, k, ch):
    value = float(self.txtV[k][ch].text())
    print("mod : " +  str(modIndex[k]) + ", ch : " + str(ch) + " | " +  str(value))
    mpod.SetHV( modIndex[k]*100 + ch, value)
    newValue = mpod.GetHV(modIndex[k]*100+ch)
    self.txtV[k][ch].setText("{:.1f}".format(newValue))

  def SetI(self, k, ch):
    value = float(self.txtI[k][ch].text())
    print("mod : " +  str(modIndex[k]) + ", ch : " + str(ch) + " | " +  str(value))
    mpod.SetCurrent( modIndex[k]*100 + ch, value/1e6)
    newValue = mpod.GetCurrent(modIndex[k]*100+ch) * 1e6
    self.txtI[k][ch].setText("{:.2f}".format(newValue))

  def SwitchOnAllCh(self):
    for k in range(0, nMod):
      for ch, a in enumerate(modChList[k]) :
        state = self.chkON[k][ch].checkState()
        if state !=  Qt.CheckState.Checked:
          print("Switching On Mod-%d, ch-%d" % (k, ch))
          mpod.SwitchOnHV( int(k) * 100 + int(ch), 1)
          self.chkON[k][ch].setChecked(True)
          onOffList[sum(nChPerMod[:k]) + ch] = 1
          time.sleep(0.01) # wait 10 mili-sec

    print("========== done")

  def SwitchOffAllCh(self):
    for k in range(0, nMod):
      for ch, a in enumerate(modChList[k]) :
        state = self.chkON[k][ch].checkState()
        if state ==  Qt.CheckState.Checked:
          print("Switching off Mod-%d, ch-%d" % (k, ch))
          mpod.SwitchOnHV( int(modIndex[k]) * 100 + int(ch), 0)
          self.chkON[k][ch].setChecked(False)
          onOffList[sum(nChPerMod[:k]) + ch] = 0
          time.sleep(0.01) # wait 10 mili-sec

    print("========== done")

  def SetOnOff(self, k, ch):
    state = self.chkON[k][ch].checkState()
    if state ==  Qt.CheckState.Checked:
      if onOffList[sum(nChPerMod[:k]) + ch] == 3 :
        mpod.SwitchOnHV(modIndex[k]*100 + ch, 2)
      mpod.SwitchOnHV( modIndex[k]*100 + ch, 1)
      onOffList[sum(nChPerMod[:k]) + ch] = 1
    else:
      mpod.SwitchOnHV( modIndex[k]*100 + ch, 0)
      onOffList[sum(nChPerMod[:k]) + ch] = 0

    value = mpod.IsHVOn(modIndex[k]*100 + ch)
    print("mod : " +  str(modIndex[k]) + ", ch : " + str(ch) + " | " +  str(state) + " | " + str(onOffList[sum(nChPerMod[:k]) + ch]) + " | " + str(value))
    if value == 0 :
      self.chkON[k][ch].setChecked(False)
      self.chkON[k][ch].setStyleSheet("")
    if value == 1 :
      self.chkON[k][ch].setChecked(True)
      self.chkON[k][ch].setStyleSheet("")
    if value == 3 :
      self.chkON[k][ch].setChecked(False)
      self.chkON[k][ch].setStyleSheet("background-color: red;")
 
  def updateTimer(self):
    # self.time += 1
    # print(f'Time: {self.time}')
    outVList = mpod.GetAllOutputHV()
    outIList = mpod.GetAllLC() 
    # print(outVList)

    if self.chkDB.checkState() == Qt.CheckState.Checked:
      points = []

    for k in range(0, nMod):
      for i, a in enumerate(modChList[k]) :

        vout = outVList[sum(nChPerMod[:k]) + i] # in Volt
        iout = outIList[sum(nChPerMod[:k]) + i] # in Amp
        self.txtVOut[k][i].setText("{:.2f}".format(vout))
        self.txtIOut[k][i].setText("{:.2f}".format(iout * 1e6))

        if self.chkDB.checkState() == Qt.CheckState.Checked:
          points.append(Point("Voltage").tag("Ch",int(chList[i] + 100 * k)).field("value",float(outVList[sum(nChPerMod[:k]) + i])))
          points.append(Point("LeakageCurrent").tag("Ch",int(chList[i] + 100 * k)).field("value",float(outIList[sum(nChPerMod[:k]) + i])))

    if self.chkDB.checkState() == Qt.CheckState.Checked:
      
      write_api.write(bucket=bucket, org=org, record=points)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MyWindow()
  window.show()
  sys.exit(app.exec())
