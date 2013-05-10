#!/bin/bash 

. config.sh

ssh $MAILMAN 'for l in $(list_lists | grep " - " | awk "{print \$1}"); do for m in $(list_members $l); do echo $l $m; done; done'
