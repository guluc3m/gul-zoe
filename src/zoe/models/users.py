import configparser

class Users:
    def __init__(self, conffile = "zoe-users.conf", confstring = None):
        self._conffile = conffile
        self._confstring = confstring
        self.update()

    def update(self): 
        self._config = configparser.ConfigParser()
        if self._conffile:
            self._config.read(self._conffile, encoding = "utf8")
        else:
            self._config.read_string(self._confstring, encoding = "utf8")
            
    def asmap(self):
        users = {}
        users["subject"] = []
        for section in self._config.sections():
            kind, name = section.split(" ")
            if kind == "group":
                for key in self._config[section]:
                    key2 = "group-" + name + "-" + key
                    value2 = self._config[section][key]
                    if key == "members":
                        value2 = value2.split()
                    users[key2] = value2
            else:
                users["subject"].append(name)
                for key in self._config[section]:
                    users[name + "-" + key] = self._config[section][key]
        return users

    def subjects(self):
        ids = {} 
        for section in self._config.sections():
            kind, name = section.split(" ")
            if kind == "subject":
                aMap = {}
                for key in self._config[section]:
                    aMap[key] = self._config[section][key]
                ids[name] = aMap
        return ids

    def subject(self, name):
        return self._config["subject " + name]

    def group(self, name):
        return self._config["group " + name]
