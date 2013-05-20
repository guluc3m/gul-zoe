#!/bin/bash

. common.sh

# The user we are looking for
USER="$1"
USER=`sanitize "$USER"`

# choose a random CID
CID=`genuid`

# Query parameters
SRC="users"
TOPIC="users"
M="dst=users&tag=notify&_cid=$CID"

# Execute query
pushd $ZOE_BASE >/dev/null
$PYTHON3 stalker_agent.py -s "$SRC" -t "$TOPIC" -m "$M" | grep "^$USER-"
popd >/dev/null
