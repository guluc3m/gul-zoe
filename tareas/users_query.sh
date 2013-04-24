#!/bin/bash

. common.sh

# The user we are looking for
USER="$1"
USER=`sanitize "$USER"`

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

# show the user info
cat $TEMPFILE | grep "^$USER-"
rm $TEMPFILE
