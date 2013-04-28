#!/bin/bash 

. config.sh

pushd $ZOE_BASE >/dev/null
echo -n "" > $ZOE_PIDS

function launch() {
    NAME=$1
    SCRIPT=$2
    echo "Starting $NAME"
    LOG=$ZOE_LOGS/$NAME.log
    ERR=$ZOE_LOGS/$NAME.error.log
    $PYTHON3 $SCRIPT > $LOG 2>$ERR &
    PID=$!
    echo $PID >> $ZOE_PIDS
    sleep 1
}

launch server server.py

for AGENT in $ENABLED_AGENTS
do
    launch $AGENT ${AGENT}_agent.py
done

