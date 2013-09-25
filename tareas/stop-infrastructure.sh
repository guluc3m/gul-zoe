#!/bin/bash 

. config.sh

for PID in `cat $ZOE_PIDS`
do
    echo "Stopping PID $PID"
    pkill -P $PID
    kill $PID
done

