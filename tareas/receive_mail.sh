#!/bin/bash

. common.sh

ID=`genuid`
BODY="/tmp/$ID"
SCRIPT=${BODY}_script
trap "rm $BODY $SCRIPT" 0

cat - > $BODY
B64=`cat $BODY | base64`

cd $MAILPROC
for proc in $(find . -type f)
do
	$proc $BODY >> $SCRIPT
done

while read line
do
	echo Sending message $line
	send "$line"
done < $SCRIPT

#MSG="dst=mail&tag=received&body=$BODY"
