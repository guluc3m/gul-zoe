#!/bin/bash

. common.sh

M=`sanitize "$1"`
MSG="dst=broadcast&tag=send&msg=$M"
send "$MSG"

