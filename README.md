# IsegSNMPGUI

Python-based HV control and monitoring suite for **Iseg MPOD** crates via SNMP (WIENER-CRATE-MIB).

Developed at FSU; adapted for ANL HELIOS (`HELIOS` branch).

---

## Files

| File | Description |
|---|---|
| `IsegLibrary.py` | Core SNMP interface — `Mpod` class (get/set HV, current, on/off, rise/fall rates) |
| `IsegGUI.py` | Qt6 GUI for interactive HV control and monitoring |
| `IsegMonitor.py` | Headless daemon — polls all channels, pushes to InfluxDB (HELIOS Pi use) |
| `IsegHVController.py` | Legacy PySimpleGUI — **not maintained**, kept for reference only |
| `IsegHVDataBase.py` | Database helper (legacy) |
| `DataBase_test.py` | Database connection test script |

---

## Dependencies

### Ubuntu / Raspberry Pi OS

```bash
sudo apt install snmp snmp-mibs-downloader python3-pip
pip3 install influxdb-client
# For GUI only:
sudo apt install python3-pyqt6 libxcb-cursor0
pip3 install pyqt6
```

### macOS

```bash
brew install net-snmp
pip3 install influxdb-client pyqt6
# If system snmp conflicts with homebrew:
export PATH="/usr/local/opt/net-snmp/bin/:$PATH"
```

### WIENER-CRATE-MIB

Download from: https://fsunuc.physics.fsu.edu/wiki/images/5/53/WIENER-CRATE-MIB.txt

Place in:
- **Linux/Pi:** `/usr/share/snmp/mibs/`
- **macOS (homebrew):** `/usr/local/share/snmp/mibs/` (or homebrew snmp share folder)

---

## Usage

### GUI (interactive)

```bash
python3 IsegGUI.py [IP]
# default IP: 192.168.1.155
```

Displays all MPOD channels grouped by module. Supports:
- Per-channel and all-module HV/current set
- On/off switching
- Rise/fall rate control
- CSV save/load of channel settings
- Optional live InfluxDB push

### Headless Monitor Daemon (HELIOS Pi)

`IsegMonitor.py` runs continuously in the background, polling all HV channels every 3 seconds and pushing to InfluxDB v1.

```bash
cd ~/IsegSNMPGUI
nohup python3 -u IsegMonitor.py >> /tmp/iseg_monitor.log 2>&1 &
```

Stop:
```bash
pkill -f IsegMonitor.py
```

Check log:
```bash
tail -f /tmp/iseg_monitor.log
```

Features:
- Single-instance lock (port 4355) — prevents duplicate daemons
- Graceful shutdown on SIGINT/SIGTERM
- Auto-reconnect after 5 consecutive MPOD communication failures
- Pushes `HV` (measured voltage, V) and `LC` (leakage current, µA) measurements
- Tags: `Det` (channel % 100), `Module` (channel // 100)

---

## HELIOS Setup (ANL Pi — `192.168.1.100`)

| Parameter | Value |
|---|---|
| MPOD IP | `192.168.1.155` |
| InfluxDB | `http://192.168.1.193:8086` (v1, no auth) |
| DB name | `testing` |
| Poll interval | 3 seconds |

MPOD channel layout:
- **Module 0** (`u0`–`u15`): Array Left / Bottom / Right detectors
- **Module 2** (`u200`–`u215`): Array Right / Top detectors  
- **Module 3** (`u300`–`u315`): RDT dE / E detectors

CSV mapping file: `~/IsegSNMPGUI/h095.csv` — format: `Name, channel, SetV, SetI`

---

## InfluxDB

### v1 (HELIOS Pi → Mac at 192.168.1.193)
No token needed. `IsegMonitor.py` uses the v1 compatibility endpoint:
```
bucket = "<db_name>/"
```

### v2 (FSU — legacy)
Token required. See: https://fsunuc.physics.fsu.edu/elog/fsunuc/28

---

## HV Safety Rules ⚠️

- **Ramp in 10–20 V steps** — never jump to final voltage in one command
- **Check leakage current after every step** — if > 2 µA, stop and hold
- **Always report both** measured voltage AND leakage current after each set
- `SwitchOnHV` always sends `i 10` (arm) before the actual on/off value — this is intentional hardware behavior

---

## Branch Notes

- **`main`**: General-purpose, FSU-oriented
- **`HELIOS`**: ANL HELIOS spectrometer — includes `IsegMonitor.py` headless daemon and HELIOS-specific configuration
