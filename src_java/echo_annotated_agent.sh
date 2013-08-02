#!/bin/bash

LAUNCHER=es.gul.zoe.AnnotatedAgentLoader
AGENTS=org.voiser.zoe.AnnotatedEchoAgent
DEBUG="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=40000"

java $DEBUG -cp $ZOE_HOME/src_java/lib/\*:$ZOE_HOME/src_java/libzoe/\* $LAUNCHER $AGENTS

