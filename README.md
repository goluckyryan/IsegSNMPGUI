# Request packages

in Ubuntu 20+

    ~>sudo apt install python3-tk snmp snmp-mibs-downloader curl python3-pip
    ~>python3 -m pip install pysimplegui influxdb-client

also, download the https://fsunuc.physics.fsu.edu/wiki/images/5/53/WIENER-CRATE-MIB.txt and put in /usr/share/snmp/mibs/


# Usage

    ~>python3 IsegHVController.py <IP>

# DataBase connection

for influxDB V1, simply put the database IP. since 2024, we upgraded to influxDB V2, a token is needed for secure connection. For Token, please check https://fsunuc.physics.fsu.edu/elog/fsunuc/28