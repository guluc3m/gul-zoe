JAR=zoe-twitter-agent.jar
SHELL=/bin/bash

all: jar

dirs:
	mkdir -p build/{tmp,classes,testclasses,lib}

classes: dirs
	find src/main/java -name *.java > build/tmp/sources
	javac -cp ${ZOE_HOME}/lib/java/zoe/\*:${ZOE_HOME}/lib/java/third_party/\* -d build/classes @build/tmp/sources

jar: classes
	pushd build/classes && jar cvf ../lib/${JAR} * && popd
	cp build/lib/* ..
	@echo

clean:
	rm -rf build/
