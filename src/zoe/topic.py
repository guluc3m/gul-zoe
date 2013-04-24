
class TopicDispatcher:
    def __init__(self, config):
        self._topics = {}
        self._config = config
        self.registerTopics()

    def registerTopics(self):
        for section in self._config.sections():
            sectype, name = section.split(" ")
            if sectype == "topic":
                agents = self._config[section]["agents"].split(" ")
                self.add (name, *agents)

    def descr(self):
        return "Topic dispatcher"

    def add(self, topic, *names):
        if not topic in self._topics:
            self._topics[topic] = []
        for name in names:
            self._topics[topic].append(name)

    def remove(self, topic, *names):
        if not topic in self._topics:
            return
        for name in names:
            if name in self._topics[topic]:
                self._topics[topic].remove(name)

    def dispatch(self, parser):
        tname = parser.get("topic")
        if not tname: return None
        if not tname in self._topics: return None
        agents = list(self._topics[tname])
        src = parser.get("src")
        if src and src in agents:
            agents.remove(src)
        return agents
