# Request packages

in Ubuntu 20+

    ~>sudo apt install python3-pyqt6 snmp snmp-mibs-downloader curl python3-pip libxcb-cursor0
    ~>python3 -m pip install pyqt6 influxdb-client

also, download the https://fsunuc.physics.fsu.edu/wiki/images/5/53/WIENER-CRATE-MIB.txt and put in /usr/share/snmp/mibs/


# Usage

    ~>python3 IsegGUI.py <IP>

# DataBase connection

for influxDB V1, simply put the database IP. since 2024, we upgraded to influxDB V2, a token is needed for secure connection. For Token, please check https://fsunuc.physics.fsu.edu/elog/fsunuc/28

# old GUI using PySimpleGUI

Since the PySimpleGUI think user should register, so We use Qt6. The IsegHVController.py is no longer maintain.
