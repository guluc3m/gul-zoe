#!/bin/bash 

. config.sh

pushd $ZOE_BASE >/dev/null

RUNNING=""
STOPPED=""

function check() {
    NAME=$1
    SCRIPT=$2
    WORKING=`ps ax | grep $SCRIPT | grep -v grep | wc -l`
    if [ "$WORKING" -eq "1" ]
    then 
        RUNNING="$RUNNING $NAME"
    else
        STOPPED="$STOPPED $NAME"
    fi
}

check server server.py

for AGENT in $ENABLED_AGENTS
do
    check $AGENT ${AGENT}_agent.py
done

echo "Running:"
for AGENT in $RUNNING
do
    echo "    $AGENT"
done

echo
echo "Stopped:"
for AGENT in $STOPPED
do
    echo "    $AGENT"
done

