#!/bin/bash 

. config.sh

pushd $ZOE_BASE >/dev/null

for PID in `cat $ZOE_PIDS`
do
    echo "Stopping PID $PID"
    pkill -P $PID
    kill $PID
done

