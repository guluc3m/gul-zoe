JAR=zoe.jar

all: test jar

dirs:
	mkdir -p build/{tmp,classes,testclasses,lib}

classes: dirs
	find src/main/java -name *.java > build/tmp/sources
	javac -cp '../third_party/*' -d build/classes @build/tmp/sources

testClasses: classes
	find src/test/java -name *.java > build/tmp/testsources
	javac -cp '../third_party/*:../third_party_test/*:build/classes' -d build/testclasses @build/tmp/testsources

test: testClasses
	java -cp '../third_party/*:../third_party_test/*:build/classes:build/testclasses' org.junit.runner.JUnitCore es.gul.zoe.test.SmokeTest es.gul.zoe.test.AnnotationsTest

jar: classes
	pushd build/classes && jar cvf ../lib/${JAR} * && popd
	cp build/lib/* .
	@echo

clean:
	rm -rf build/
