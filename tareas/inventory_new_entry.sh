#!/bin/bash

. common.sh

AMOUNT=$1
WHAT=$2

AMOUNT=`sanitize $AMOUNT`
WHAT=`sanitize $WHAT`

MSG="dst=inventory&tag=entry&amount=$AMOUNT&what=$WHAT"

send "$MSG"

