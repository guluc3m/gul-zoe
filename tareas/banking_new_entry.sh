#!/bin/bash

. common.sh

YEAR=$1
DATE=$2
AMOUNT=$3
WHAT=$4

YEAR=`sanitize "$YEAR"`
DATE=`sanitize "$DATE"`
AMOUNT=`sanitize "$AMOUNT"`
WHAT=`sanitize "$WHAT"`

MSG="dst=banking&tag=entry&year=$YEAR&date=$DATE&amount=$AMOUNT&what=$WHAT"

send "$MSG"

