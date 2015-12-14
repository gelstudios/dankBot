#!/usr/bin/env python
# hipchat imgur + giphy + goog + etc bot

from bottle import Bottle, run, get, post, request

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

import requests

import giphypop

import json
import os
import datetime
import random

imgur_id = os.environ.get('imgur_id', None)
imgur_secret = os.environ.get('imgur_secret', None)

def imgur_search(search=""):
    try:
        client = ImgurClient(imgur_id, imgur_secret)
    except ImgurClientError as e:
        if e.status_code == 403:
            return u'can i haz valid api keys?'
        else:
            return u'sorry i could not reach imgur :/  E_MSG: {0} E_CODE: {1}'.format(e.error_message, e.status_code)
    try:
        items = client.gallery_search(search, advanced=None, sort='time', window='all', page=0)
    except ImgurClientError as e:
        return u'derp, something bad happened: {0}'.format(e.error_message)

    if len(items) > 0:
        item = items[0]
        if item.is_album:
            try:
                items = client.get_album_images(item.id)
            except ImgurClientError as e:
                return u'derp, something bad happened: {0}'.format(e.error_message)
        item = items[0]
        item = item.link
    else:
        item = u'i got nothing for "{0}", bro'.format(search)
    return item

    # print "tag search"
    # items = client.gallery_tag("datto", sort='viral', page=0, window='week')
    # print dir(items.items[0])

def giphy_search(search=""):
    try:
        client = giphypop.Giphy()
    except Exception as e:
        return u'sorry i could not reach giphy :/ E_MSG: {0}'.format(e)

    try:
        items = client.search_list(phrase=search)
    except Exception as e:
        return u'derp, something bad happened: {0}'.format(e)

    if items:
        item = items[0]
        item = item.fixed_height.url
    else:
        item = u'i got nothing for "{0}", bro'.format(search)
    return item

def google_search(search=""):
    # req = requests.url("google.com/somesearch/string")
    # try:
    #     items = req.get()
    #     item = items[0]
    # except Exception as e:
    item = u'i got nothing for "{0}", bro'.format(search)
    return item

def dankify(words):
    """ /dankify message here! -> returns (m)(e)(s)(s)(a)(g)(e)(space)(h)(e)(r)(e)(bang) """
    dank = [ "(space)" if w == " " else "(bang)" if w == "!" else "({0})".format(w) for w in words ]
    dank = "".join(dank)
    return dank

def dev(command, who):
    print "[dankBot] DEV: {0} USR: {1}".format(repr(command), who)
    return "dev mode: up up down down left right left right a b start"

app = Bottle()

@app.route('/stats')
def stats():
    client = ImgurClient(imgur_id, imgur_secret)
    # looks like {u'UserLimit': 500, u'UserRemaining': 500, u'UserReset': 1449849295, u'ClientLimit': 12500, u'ClientRemaining': 11351}
    template = (
    "<html><body>"
    "---Imgur API info---<br>"
    "Total credits that can be allocated: {UserLimit}<br>"
    "Total credits available: {UserRemaining}<br>"
    "Timestamp (unix epoch) for when the credits will be reset. {UserReset}<br>"
    "Total credits that can be allocated for the application in a day: {ClientLimit}<br>"
    "Total credits remaining for the application in a day: {ClientRemaining}<br>"
    "</body></html>")
    return template.format(**client.credits)

@app.route('/capabilities.json')
def caps():
    with open("capabilities.json", "r") as f:
        c = f.read()
    return c

@app.route('/', method='POST')
def handle():
    derp = request.json
    msg = derp[u'item'][u'message'][u'message']
    room = derp[u'item'][u'room'][u'name']
    who = derp[u'item'][u'message'][u'from'][u'mention_name']

    m = msg.split()

    command = m[0]
    parsed = m[1:]

    # basic logic for multiple slash-commands
    if command == u'/dank':
        message = imgur_search(search=" ".join(parsed))
    elif command == u'/dankify':
        message = dankify(" ".join(parsed))
    elif command == u'/dankdev':
        message = dev(" ".join(parsed), who)
    elif command == u'/jank':
        message = giphy_search(search=" ".join(parsed))
    elif command == u'/gank':
        message = google_search(search=" ".join(parsed))
    elif command == u'/halp':
        message = "bro use /dank for imgur, /jank for giphy, /gank for goog"
    else:
        message = "welp! command not found: {0}".format(command)

    if who == u'RyanPineau' and random.randint(0,100) == 1:
        message = "/me thinks @{0} needs to shut the f up...".format(who)

    resp = {"color":"random",
            "message": message,
            "notify": False,
            "message_format":"text"}
    # log-message
    print("[dankBot] room={0} who={1} cmd={2} parsed={3} msg={4}").format(room, who, command, parsed, message)

    return json.dumps(resp)

@app.route('/', method='GET')
def index():
    template = (
    "<html><body>"
    "dankBot for hipchat by @gelstudios<br>"
    "<br>"
    "The dankest bot in all the land.<br>"
    "Implements handlers: /dank for imgur, /jank for giphy, /gank for google, /halp for help<br>"
    "To install use this as the integration URL: <pre>http://imgur-hipchat.herokuapp.com/capabilities</pre><br>"
    "TODO: make api keys easier to manage, implement google_search() handler"
    "</body></html>")
    return template

if __name__=="__main__":
    port = os.environ.get('PORT', 8080)
    run(app, port=port, host='0.0.0.0')
