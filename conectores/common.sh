#!/bin/bash

SERVER_HOST=localhost
SERVER_PORT=30000
PYTHON32=python3.2
ZOE_BASE="../src"

function sanitize() {
    echo "$1" | tr '&=' '.'
}

function send() {
    MSG="$1"
    echo -n "$MSG" | nc $SERVER_HOST $SERVER_PORT
}

function stalk() {
    SRC="$1"
    TOPIC="$2"
    CID="$3"
    pushd $ZOE_BASE >/dev/null
    $PYTHON32 stalker_agent.py --cid $CID --src $SRC --topic $TOPIC
    popd >/dev/null
}

