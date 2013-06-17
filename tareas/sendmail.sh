#!/bin/bash
#
#TEXT="esto va en claro"a
if [ "$#" -lt "2" ];then
	exit 1;
fi
CUERPO="$(mktemp)"
trap "rm $CUERPO" 0

cat - > $CUERPO
SUBJECT="$1"
LONGB64="$(base64 -w 0 $CUERPO)"
shift

while [ "$1" ];do
	TO="$1"
	shift
	MSG="dst=mail&to=$TO&subject=$SUBJECT&txt64=text/plain;file.txt:$LONGB64"
	echo -n "$MSG" | nc localhost 30000
done
