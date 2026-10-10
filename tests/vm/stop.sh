#!/bin/bash
# Copyright (c) 2026 Nicola Fiorillo
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# RootSpeak - Advanced Messaging System for Linux
# Runs on the test server: shuts the test VM down and deletes its working disk.
#   stop.sh VM_FOLDER
DIR=$1
if [ -f "$DIR/test.pid" ]; then
	pid=$(cat "$DIR/test.pid")
	kill "$pid" 2>/dev/null
	for i in $(seq 1 20); do kill -0 "$pid" 2>/dev/null || break; sleep 0.5; done
	rm -f "$DIR/test.pid"
fi
rm -f "$DIR/test.qcow2" "$DIR/monitor.sock"
