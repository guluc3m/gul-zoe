#!/bin/bash

. config.sh

function sanitize() {
    echo "$1" | tr '&=' '.'
}

function send() {
    MSG="$1"
    echo -n "$MSG" | nc $ZOE_SERVER_HOST $ZOE_SERVER_PORT
}

function genuid() {
    if [ "`uname`" == "Linux" ] 
    then
        uuid
    else
        uuidgen
    fi
}
