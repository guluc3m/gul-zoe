#!/bin/bash

. common.sh

DATE=$1
AMOUNT=$2
WHAT=$3

DATE=`sanitize $DATE`
AMOUNT=`sanitize $AMOUNT`
WHAT=`sanitize $WHAT`

MSG="dst=banking&tag=entry&date=$DATE&amount=$AMOUNT&what=$WHAT"

send "$MSG"

