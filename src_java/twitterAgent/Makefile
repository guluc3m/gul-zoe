JAR=zoe-twitter-agent.jar

all: jar

dirs:
	mkdir -p build/{tmp,classes,testclasses,lib}

classes: dirs
	find src/main/java -name *.java > build/tmp/sources
	javac -cp '../lib/*:../libzoe/*' -d build/classes @build/tmp/sources

jar: classes
	pushd build/classes && jar cvf ../lib/${JAR} * && popd
	cp build/lib/* ../libzoe
	@echo
	@echo "The final jar has been copied to ${ZOE_HOME}/src_java/libzoe/${JAR}"

clean:
	rm -rf build/
