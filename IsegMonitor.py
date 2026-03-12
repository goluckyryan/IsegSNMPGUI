#!/usr/bin/python3
# IsegMonitor.py - Headless HV monitor daemon for HELIOS Pi
# Reads all HV channel voltages + leakage currents from Iseg MPOD
# and pushes to InfluxDB v1 at 192.168.1.193 continuously.
# Based on IsegGUI.py by goluckyryan — no GUI, no PyQt6 required.

import sys
import time
import signal
import socket
from datetime import datetime

import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Add IsegSNMPGUI dir to path so we can import IsegLibrary
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import IsegLibrary as iseg

# ---- Config ----
HV_IP      = "192.168.1.155"
DB_IP      = "http://192.168.1.193:8086"
DB_NAME    = "testing"   # InfluxDB v1 database name (used as bucket)
UPDATE_SEC = 3           # seconds between each poll

# ---- InfluxDB v1 client (no token needed for v1) ----
write_client = InfluxDBClient(url=DB_IP, token="", org="")
write_api = write_client.write_api(write_options=SYNCHRONOUS)

# ---- Single-instance lock via socket ----
lock_sock = socket.socket()
lock_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    lock_sock.bind(("localhost", 4355))
except OSError:
    print("ERROR: IsegMonitor is already running (port 4355 in use). Exiting.")
    sys.exit(1)

# ---- Graceful shutdown ----
running = True
def _handle_signal(sig, frame):
    global running
    print(f"\n[{datetime.now()}] Signal {sig} received — shutting down.")
    running = False

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

# ---- Connect to MPOD ----
print(f"[{datetime.now()}] Connecting to Iseg MPOD at {HV_IP}...")
mpod = iseg.Mpod(HV_IP)
if not mpod.isConnected:
    print("ERROR: Cannot connect to MPOD. Exiting.")
    sys.exit(1)

chList = mpod.GetChList()
print(f"[{datetime.now()}] Connected. Channels: {chList}")
print(f"[{datetime.now()}] Pushing to InfluxDB v1 at {DB_IP} every {UPDATE_SEC}s")

# ---- Main loop ----
while running:
    try:
        outVList = mpod.GetAllOutputHV()   # measured voltage [V]
        outIList = mpod.GetAllLC()          # leakage current [A]

        points = []
        for i, ch in enumerate(chList):
            det    = ch % 100
            module = ch // 100
            points.append(Point("HV").tag("Det", det).tag("Module", module).field("value", float(outVList[i])))
            points.append(Point("LC").tag("Det", det).tag("Module", module).field("value", float(outIList[i] * 1e6)))

        write_api.write(bucket=f"{DB_NAME}/", org="", record=points)

        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] Pushed {len(chList)} channels to InfluxDB ✅")

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")

    time.sleep(UPDATE_SEC)

print(f"[{datetime.now()}] IsegMonitor stopped.")
