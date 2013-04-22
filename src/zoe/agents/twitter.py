from zoe import *
import tweepy

class TwitterAgent:
    def __init__(self, host, port, serverhost, serverport, \
                 consumer_key, consumer_secret, access_token, access_token_secret):
        self._listener = Listener(host, port, self, serverhost, serverport)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self._api = tweepy.API(auth)
        print ("Using account: " + self._api.me().name)
        # TODO: check connection

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def receive(self, parser):
        to = parser.get("to")
        msg = parser.get("msg")
        print ("Sending " + msg + " to @" + to)
        status = "@" + to + " " + msg
        # TODO check status length
        self._api.update_status(status)
