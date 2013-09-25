#!/bin/bash

. common.sh

CMD="$1"
CMD=`sanitize "$CMD"`

ID=`genuid`
TMP="/tmp/fuzzy-$ID"

pushd $ZOE_BASE >/dev/null
$PYTHON3 fuzzy.py "$CMD" > $TMP
STATUS=$?
popd >/dev/null

cat $TMP
exit $STATUS
