#!/usr/bin/env python3
"""AMS - Advanced Messaging System
Gira sul server delle prove: cattura lo schermo della VM di prova dal monitor di
QEMU (formato PPM).    capture.py SOCKET_MONITOR FILE.ppm"""
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
