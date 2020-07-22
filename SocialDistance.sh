#!/bin/bash
echo BD/report Server start
nohup python3 report.py &
echo Track System start
nohup python3 pysyslog.py &
nohup python3 syslog_parsing.py &
nohup python3 trigger.py &
echo Mask Detection start
nohup python3 app.py &
echo Social Bot start 
nohup socialbot.py &
