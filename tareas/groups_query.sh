#!/bin/bash

. common.sh

# The group we are looking for
GROUP="$1"
GROUP=`sanitize "$GROUP"`

# choose a random CID
CID=`uuidgen`

# stalk the "users" topic, and wait for a message from agent "users"
SRC="users"
TOPIC="users"
TEMPFILE="/tmp/zoe-stalk.tmp"
stalk "$SRC" "$TOPIC" "$CID" > $TEMPFILE &
PID=$!
sleep 1

# inject a query message
M="dst=users&tag=notify&_cid=$CID"
send "$M"

# wait for the stalker
wait $PID

# show the group info
cat $TEMPFILE | grep "^group-$GROUP-"
rm $TEMPFILE
