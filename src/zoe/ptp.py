
class PTPDispatcher:
    def __init__(self, config = None):
        pass

    def descr(self):
        return "Point-to-point dispatcher"

    def dispatch(self, parser):
        if parser.get("dst"):
            return parser.get("dst")

