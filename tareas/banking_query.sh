#!/bin/bash

. common.sh

YEAR="$1"
YEAR=`sanitize "$YEAR"`

# choose a random CID
CID=`uuidgen`

# Query parameters
SRC="banking"
TOPIC="banking"
M="dst=banking&tag=notify&year=$YEAR&_cid=$CID"

# Execute query
TEMP=/tmp/$CID
pushd $ZOE_BASE >/dev/null
$PYTHON3 stalker_agent.py -s "$SRC" -t "$TOPIC" -m "$M" > $TEMP
popd >/dev/null

IDS=`cat $TEMP | grep -- "-amount" | sed -e 's/-amount.*//'`
for i in $IDS
do
    date=`cat $TEMP | grep "^$i-date" | sed -e "s/^.*=//"`
    amount=`cat $TEMP | grep "^$i-amount" | sed -e "s/^.*=//"`
    what=`cat $TEMP | grep "^$i-what" | sed -e "s/^.*=//"`
    echo $date $amount $what
done

cat $TEMP | grep "^balance"


