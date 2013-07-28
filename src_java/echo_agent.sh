#!/bin/bash

LAUNCHER=es.gul.zoe.AgentLoader
AGENTS=org.voiser.zoe.EchoAgent
DEBUG="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=40000"

java -cp $ZOE_HOME/src_java/lib/\* $LAUNCHER $AGENTS

