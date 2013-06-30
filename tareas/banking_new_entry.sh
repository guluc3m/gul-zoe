#!/bin/bash

. common.sh

YEAR="$1"
DATE="$2"
ACCOUNT="$3"
AMOUNT="$4"
WHAT="$5"

YEAR=`sanitize "$YEAR"`
DATE=`sanitize "$DATE"`
ACCOUNT=`sanitize "$ACCOUNT"`
AMOUNT=`sanitize "$AMOUNT"`
WHAT=`sanitize "$WHAT"`

MSG="dst=banking&tag=entry&year=$YEAR&date=$DATE&account=$ACCOUNT&amount=$AMOUNT&what=$WHAT"

send "$MSG"

