#!/usr/bin/env bash
set -x 
cd /home/pi
python3 data_gathering/timed_capture.py trainingImages/ &> trainingDebug/"debug.$(date +%b-%d-%a)"
