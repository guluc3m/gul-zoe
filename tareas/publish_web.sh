#!/bin/bash

FILE=$1
CATEGORY=gul

pushd $zoe_web > /dev/null

git reset --hard HEAD
git pull origin master
ID=`uuid`
bash newstory.sh $CATEGORY $ID
cp "$FILE" "stories/$CATEGORY/$ID"
make all test
git push origin master
