#!/bin/bash

. common.sh

ID=$1
AMOUNT=$2

ID=`sanitize $ID`
AMOUNT=`sanitize $AMOUNT`

MSG="dst=inventory&tag=update&amount=$AMOUNT&id=$ID"

send "$MSG"

