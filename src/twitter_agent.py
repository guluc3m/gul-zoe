import zoe
import os
import sys
import tweepy

consumer_key=os.environ['zoe_twitter_consumer_key']
consumer_secret=os.environ['zoe_twitter_consumer_secret']
access_token=os.environ['zoe_twitter_access_token']
access_token_secret=os.environ['zoe_twitter_access_token_secret']

agent = zoe.TwitterAgent("localhost", 30105, "localhost", 30000, \
                         consumer_key, consumer_secret, access_token, access_token_secret)
agent.start()

