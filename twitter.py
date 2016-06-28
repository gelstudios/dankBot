#!/usr/bin/env python
from twython import Twython
import os

# APP_KEY = os.environ.get('twitter_app_key', None)
# APP_SECRET = os.environ.get('twitter_app_secret', None)
# OAUTH_TOKEN = os.environ.get('twitter_oauth_token', None)
# OAUTH_TOKEN_SECRET = os.environ.get('twitter_token_secret', None)
APP_KEY = 'MtWZBornAUUpKkZFA5uEQOUe80BAl5aKallA93vM0FyRpjQag3'
APP_SECRET = 'xPb1nEwIzvYxCfqdGviPavwnF'
OAUTH_TOKEN = '723720744052637696-KaFyoqq8VQWc5cU88GvsbYF3rT42bI3'
OAUTH_TOKEN_SECRET = 'MWejBj3jvCyC3Qx2TLLUmXFjZoBZZwUm2k8RAdmauCJKC'

TWITTER_API = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def tweet_message(message=''):
    if message == '':
        return 'Bro, you forgot a message. Shits important yo'
    elif len(message) > 140:
        return 'Bro, this is too much. I can\'t tweet this'
    else:
        tweet = TWITTER_API.update_status(message)
        print tweet['id_str']
        return ''


tweet_message("hello world")
