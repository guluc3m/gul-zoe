#!/bin/bash

SERVER_HOST=localhost
SERVER_PORT=30000

function sanitize() {
    echo "$1" | tr '&=' '.'
}

function send() {
    MSG="$1"
    echo -n "$MSG" | nc $SERVER_HOST $SERVER_PORT
}

