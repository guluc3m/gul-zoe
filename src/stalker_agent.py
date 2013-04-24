import zoe
import sys
import getopt

def usage():
    print ("Usage: python3.2 " + sys.argv[0] + " [options]")
    print ("    Options:")
    print ("        --help         Shows this help")
    print ("        -s, --src      Source of the message to intercept")
    print ("        -c, --cid      Correlation ID of the message to intercept")
    print ("        -t, --topic    Topic to listen for the message")

argv = sys.argv[1:]
source = None
cid = None
topic = None

try:
    opts, args = getopt.getopt(argv, "hs:c:t:", ["help", "src=", "cid=", "topic="])
except Exception as e:
    usage()
    sys.exit(1)

for opt, arg in opts:
    if opt in ("-s", "--src"):
        source = arg
    if opt in ("-c", "--cid"):
        cid = arg
    if opt in ("-t", "--topic"):
        topic = arg
    if opt in ("-h", "--help"):
        usage()
        sys.exit(0)

agent = zoe.StalkerAgent("localhost", 0, "localhost", 30000, (source, cid, topic))
agent.start()

