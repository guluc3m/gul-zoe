JAR=zoe.jar

all: test jar

dirs:
	mkdir -p build/{tmp,classes,testclasses,lib}

classes: dirs
	find src/main/java -name *.java > build/tmp/sources
	javac -cp '../lib/*' -d build/classes @build/tmp/sources

testClasses: classes
	find src/test/java -name *.java > build/tmp/testsources
	javac -cp '../lib/*:build/classes' -d build/testclasses @build/tmp/testsources

test: testClasses
	java -cp '../lib/*:build/classes:build/testclasses' org.junit.runner.JUnitCore es.gul.zoe.test.SmokeTest 

jar: classes
	pushd build/classes && jar cvf ../lib/${JAR} * && popd
	cp build/lib/* ../lib/
	@echo
	@echo "The final jar has been copied to ${ZOE_HOME}/src_java/lib/${JAR}"

clean:
	rm -rf build/
