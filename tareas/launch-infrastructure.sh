#!/bin/bash

function launch() {
    NAME="$1"
    LAUNCHER="$2"
    SCRIPT="$3"
    echo "Starting $NAME"
    LOG=$ZOE_LOGS/$NAME.log
    ERR=$ZOE_LOGS/$NAME.error.log
    $LAUNCHER $SCRIPT > $LOG 2>$ERR &
    PID=$!
    echo $PID >> $ZOE_PIDS
}

# read configuration
. config.sh

# start server
pushd $ZOE_BASE >/dev/null
echo -n "" > $ZOE_PIDS
launch "server" "$PYTHON3" "server.py"
popd >/dev/null

# launch agents
DIRS="$ZOE_HOME/src $ZOE_HOME/src_java"
for DIR in $DIRS
do
    pushd $DIR > /dev/null
    for AGENT in $ENABLED_AGENTS
    do
        echo "Buscando el agente $AGENT"
        [ -f "${AGENT}_agent.py" ] && launch "$AGENT" "$PYTHON3" "${AGENT}_agent.py"
        [ -f "${AGENT}_agent.sh" ] && launch "$AGENT"  bash      "${AGENT}_agent.sh"
    done
    popd >/dev/null
done
