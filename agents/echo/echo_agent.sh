#!/bin/bash

LAUNCHER=es.gul.zoe.AgentLoader
AGENTS=org.voiser.zoe.EchoAgent
DEBUG="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=40000"
LIB=$ZOE_HOME/lib/java/zoe/\*:$ZOE_HOME/lib/java/third_party/\*

java -cp $LIB:zoe-echo-agent.jar $LAUNCHER $AGENTS

