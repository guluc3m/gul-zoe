#!/bin/bash -ex

function launch() {
    SCRIPT="$1"
    NAME="$2"
    echo "Starting $NAME"
    LOG=$ZOE_LOGS/$NAME
    ./$SCRIPT > $LOG 2>&1 &
    PID=$!
    echo $PID >> $ZOE_PIDS
}

# read configuration
. config.sh

# clean pids file
echo -n "" > $ZOE_PIDS

# start server
pushd $ZOE_HOME/server >/dev/null
#launch server server
#sleep 10
popd >/dev/null

# launch agents
for AGENT in $ENABLED_AGENTS
do
    pushd $ZOE_HOME/agents/$AGENT >/dev/null
    launch agent $AGENT
    popd >/dev/null
done

