import uuid

class MessageParser:
    def __init__(self, msg, origin = None):
        self._msg = msg.strip()
        self._map = {}
        self._origin = origin
        pairs = msg.split("&")
        for pair in pairs:
            if pair == "":
                continue
            p = pair.find("=")
            key = pair[:p]
            value = pair[p + 1:].strip()
            if key in self._map:
                current = self._map[key]
                if current.__class__ is list:
                    self._map[key].append(value)
                else:
                    self._map[key] = [current, value]
            else:
                self._map[key] = value

    def msg(self):
        return self._msg

    def get(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def tags(self):
        tags = self.get("tag")
        if tags.__class__ is list:
            return tags
        else:
            return [tags]


class MessageBuilder:

    def __init__(self, aMap, original = None):
        aStr=""
        if original:
            aMap["_cid"] = original.get("_cid")
        else:
            aMap["_cid"] = str(uuid.uuid4())
        for key in aMap.keys():
            value = aMap[key]
            if value.__class__ is str:
                aStr = aStr + key + "=" + value + "&"
            else:
                for v in value:
                    aStr = aStr + key + "=" + v + "&"
        self._msg = aStr

    def override (original, aMap):
        mp = None
        if original.__class__ is str:
            mp = MessageParser(original)
        else:
            mp = original
        newMap = dict(mp._map, **aMap)
        return MessageBuilder(newMap)

    def msg(self):
        return self._msg

