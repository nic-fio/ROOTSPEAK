#!/bin/bash
# RootSpeak - Advanced Messaging System for Linux
# Gira sul server delle prove: spegne la VM di prova e ne cancella il disco di lavoro.
#   stop.sh CARTELLA_VM
DIR=$1
if [ -f "$DIR/prova.pid" ]; then
	pid=$(cat "$DIR/prova.pid")
	kill "$pid" 2>/dev/null
	for i in $(seq 1 20); do kill -0 "$pid" 2>/dev/null || break; sleep 0.5; done
	rm -f "$DIR/prova.pid"
fi
rm -f "$DIR/prova.qcow2" "$DIR/monitor.sock"
