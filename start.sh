#!/bin/bash
cd "$(dirname "$0")"
echo "🧾 Arrancant Compres Casa Xalbi..."
sleep 0.5
open "http://localhost:8765"
python3 server.py
