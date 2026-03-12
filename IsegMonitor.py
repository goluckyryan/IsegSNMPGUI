#!/usr/bin/python3
# IsegMonitor.py - Headless HV monitor daemon for HELIOS Pi
# Reads all HV channel voltages + leakage currents from Iseg MPOD
# and pushes to InfluxDB v1 at 192.168.1.193 continuously.
# Based on IsegGUI.py by goluckyryan — no GUI, no PyQt6 required.

import os
import sys
import time
import signal
import socket
from datetime import datetime

# Add IsegSNMPGUI dir to path so we can import IsegLibrary
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import IsegLibrary as iseg

# ---- Config ----
HV_IP        = "192.168.1.155"
DB_IP        = "192.168.1.193"
DB_NAME      = "testing"
UPDATE_SEC   = 3       # seconds between each poll
OUTPUT_FILE  = "/tmp/iseg_output.txt"

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

        # Build InfluxDB line protocol
        with open(OUTPUT_FILE, "w") as f:
            for i, ch in enumerate(chList):
                det    = ch % 100
                module = ch // 100
                f.write(f"HV,Det={det},Module={module} value={outVList[i]:.4f}\n")
                f.write(f"LC,Det={det},Module={module} value={outIList[i]*1e6:.6f}\n")

        # Push to InfluxDB
        cmd = (f'curl -sS -XPOST "http://{DB_IP}:8086/write?db={DB_NAME}" '
               f'--data-binary @{OUTPUT_FILE} --speed-time 5 --speed-limit 1000')
        ret = os.system(cmd)

        ts = datetime.now().strftime("%H:%M:%S")
        if ret == 0:
            print(f"[{ts}] Pushed {len(chList)} channels to InfluxDB ✅")
        else:
            print(f"[{ts}] WARNING: curl failed (exit {ret})")

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")

    time.sleep(UPDATE_SEC)

print(f"[{datetime.now()}] IsegMonitor stopped.")
