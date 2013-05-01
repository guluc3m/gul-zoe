#!/bin/bash

. common.sh

CMD="$1"
CMD=`sanitize "$CMD"`

ID=`uuidgen`
TMP="/tmp/fuzzy-$ID"

pushd $ZOE_BASE >/dev/null
$PYTHON3 fuzzy.py "$CMD" > $TMP
popd >/dev/null

cat $TMP

