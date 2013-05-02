#!/bin/bash

. common.sh

YEAR="$1"
YEAR=`sanitize "$YEAR"`

# choose a random CID
CID=`uuidgen`

# Query parameters
SRC="courses"
TOPIC="courses"
M="dst=courses&tag=notify&year=$YEAR&_cid=$CID"

# Execute query
TEMP=/tmp/$CID
pushd $ZOE_BASE >/dev/null
$PYTHON3 stalker_agent.py -s "$SRC" -t "$TOPIC" -m "$M" > $TEMP
popd >/dev/null

IDS=`cat $TEMP | grep -- "-mindate" | sed -e 's/-mindate.*//' | sort`

for i in $IDS
do
    mindate=`cat $TEMP | grep "^$i-mindate" | sed -e "s/^.*=//"`
    maxdate=`cat $TEMP | grep "^$i-maxdate" | sed -e "s/^.*=//"`
    echo Courses from $mindate to $maxdate:
    cat $TEMP | sort | grep "^$i-lecture" | sed -e "s/^.*=/    /"
    echo
done

