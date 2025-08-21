# Request packages

## in Ubuntu 20+

    ~>sudo apt install python3-pyqt6 snmp snmp-mibs-downloader curl python3-pip libxcb-cursor0
    ~>python3 -m pip install pyqt6 influxdb-client

also, download the https://fsunuc.physics.fsu.edu/wiki/images/5/53/WIENER-CRATE-MIB.txt and put in /usr/share/snmp/mibs/

## in Mac

install snmp, also

    ~>python3 -m pip install pyqt6 influxdb-client

also put the https://fsunuc.physics.fsu.edu/wiki/images/5/53/WIENER-CRATE-MIB.txt and put in /usr/share/snmp/mibs

For homebrew snmp, need to put in homebrew snmp share folder. 

If the system already has old snmp, can replace it with the homebrew one by 

export PATH="/usr/local/opt/net-snmp/bin/:$PATH"

# Usage

    ~>python3 IsegGUI.py <IP>

if no IP is set, the default is 192.168.1.155

# DataBase connection

for influxDB V1, simply put the database IP. since 2024, we upgraded to influxDB V2, a token is needed for secure connection. For Token, please check https://fsunuc.physics.fsu.edu/elog/fsunuc/28

# old GUI using PySimpleGUI

Since the PySimpleGUI think user should register, so We use Qt6. The IsegHVController.py is no longer maintain.
