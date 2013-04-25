#!/bin/bash

. config.sh

function sanitize() {
    echo "$1" | tr '&=' '.'
}

function send() {
    MSG="$1"
    echo -n "$MSG" | nc $SERVER_HOST $SERVER_PORT
}

