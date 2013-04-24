#!/bin/bash

SERVER_HOST=localhost
SERVER_PORT=30000

DATE=$1
AMOUNT=$2
WHAT=$3

DATE=`echo $DATE | tr '&' '.' | tr '=' '.'`
AMOUNT=`echo $AMOUNT | tr '&' '.' | tr '=' '.'`
WHAT=`echo $WHAT | tr '&' '.' | tr '=' '.'`

MSG="dst=banking&tag=entry&date=$DATE&amount=$AMOUNT&what=$WHAT"

echo -n $MSG | nc $SERVER_HOST $SERVER_PORT

