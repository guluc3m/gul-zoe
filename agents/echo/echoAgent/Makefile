JAR=zoe-echo-agent.jar
TESTS=org.voiser.zoe.test.SmokeTest


all: test jar

dirs:
	mkdir -p build/{tmp,classes,testclasses,lib}

classes: dirs
	find src/main/java -name *.java > build/tmp/sources
	javac -cp ${ZOE_HOME}/lib/java/zoe/\*:${ZOE_HOME}/lib/java/third_party/\* -d build/classes @build/tmp/sources

testClasses: classes
	find src/test/java -name *.java > build/tmp/testsources
	javac -cp ${ZOE_HOME}/lib/java/zoe/\*:${ZOE_HOME}/lib/java/third_party/\*:${ZOE_HOME}/lib/java/third_party_test/\*:build/classes -d build/testclasses @build/tmp/testsources

test: testClasses
	java -cp ${ZOE_HOME}/lib/java/zoe/\*:${ZOE_HOME}/lib/java/third_party/\*:${ZOE_HOME}/lib/java/third_party_test/\*:build/classes:build/testclasses org.junit.runner.JUnitCore ${TESTS} 

jar: classes
	pushd build/classes && jar cvf ../lib/${JAR} * && popd
	cp build/lib/* ..
	@echo

clean:
	rm -rf build/
