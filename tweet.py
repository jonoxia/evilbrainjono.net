#!/usr/bin/env python

import tweepy
from blog_config import *

def updateTwitterStatus(msg):
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    api.update_status(msg)

