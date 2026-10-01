#!/usr/bin/env python3
"""RootSpeak - Advanced Messaging System for Linux
Runs on the test server: captures the screen of the test VM from the QEMU
monitor (PPM format).    capture.py MONITOR_SOCKET FILE.ppm"""
import socket
import sys
import time

s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1])
time.sleep(0.2)
s.recv(4096)
s.sendall(f"screendump {sys.argv[2]}\n".encode())
time.sleep(1.0)
s.close()
