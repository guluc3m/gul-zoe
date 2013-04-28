#!/bin/bash

. common.sh

# The group we are looking for
GRP="$1"
GRP=`sanitize "$GRP"`

# choose a random CID
CID=`uuidgen`

# Query parameters
SRC="users"
TOPIC="users"
M="dst=users&tag=notify&_cid=$CID"

# Execute query
pushd $ZOE_BASE >/dev/null
$PYTHON3 stalker_agent.py -s "$SRC" -t "$TOPIC" -m "$M" | grep "^group-$GRP-"
popd >/dev/null
