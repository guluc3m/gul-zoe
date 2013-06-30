#!/bin/bash

. common.sh

BODY=`cat | base64`
MSG="dst=mail&tag=received&body=$BODY"

send "$MSG"
