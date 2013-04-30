#!/bin/bash

. common.sh

# choose a random CID
CID=`uuidgen`

# Query parameters
SRC="inventory"
TOPIC="inventory"
M="dst=inventory&tag=notify&_cid=$CID"

# Execute query
TEMP=/tmp/$CID
pushd $ZOE_BASE >/dev/null
$PYTHON3 stalker_agent.py -s "$SRC" -t "$TOPIC" -m "$M" > $TEMP
popd >/dev/null

IDS=`cat $TEMP | grep -- "-amount" | sed -e 's/-amount.*//'`
for i in $IDS
do
    amount=`cat $TEMP | grep "^$i-amount" | sed -e "s/^.*=//"`
    what=`cat $TEMP | grep "^$i-what" | sed -e "s/^.*=//"`
    echo $i $amount $what
done

