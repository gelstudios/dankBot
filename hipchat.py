#!/usr/bin/env python
# hipchat imgur + giphy + goog + etc bot

from bottle import Bottle, run, get, post, request

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

import random
import requests

import giphypop
import googleapiclient.discovery

import json, os, datetime, random

import devcmd

imgur_id = os.environ.get('imgur_id', None)
imgur_secret = os.environ.get('imgur_secret', None)
google_api_key = os.environ.get('google_api_key', None)
google_cseid = os.environ.get('google_cseid', None)
DEBUG = os.environ.get('DEBUG', False)

state = {
    'HOTSEAT':[u'RyanPineau'],
    "RNG" : 100
    }


def search_all(search):
    message = imgur_search(search)
    if message is None:
        message = giphy_search(search)
        if message is None:
            google_search(search)
            if message is None:
                message = u'i got nothing for "{0}", bro'.format(search)
    return message


def imgur_search(search=""):
    try:
        client = ImgurClient(imgur_id, imgur_secret)
    except ImgurClientError as e:
        if e.status_code == 403:
            return u'can i haz valid api keys?'
        else:
            return u'sorry i could not reach imgur :/  E_MSG: {0} E_CODE: {1}'.format(e.error_message, e.status_code)
    try:
        search_results = client.gallery_search(search, advanced=None, sort='time', window='all', page=0)
    except ImgurClientError as e:
        return u'derp, something bad happened: {0}'.format(e.error_message)

    if len(search_results) > 0:
        item = random.choice(search_results)
        if item.is_album:
            try:
                search_results = client.get_album_images(item.id)
                item = search_results[0]
            except ImgurClientError as e:
                return u'derp, something bad happened: {0}'.format(e.error_message)

        # gifs over 10mb get returned with an h appended to their id
        # shave it off to get the full animated gif
        # alternative method
        # if item.link[-5] == 'h':
        if len(item.link) > 7:
            gif_link = item.link[0:-5]+item.link[-4:]
            if DEBUG:
                print ("""[dankBot] [DEBUG] search="{0}" Large gif link found, modifying link.""").format(search, "imgur")
        else:
            gif_link = item.link
    else:
        gif_link = None
        if DEBUG:
            print ("""[dankBot] [DEBUG] search="{0}" resource="{1}" No results found.""").format(search, "imgur")
    return gif_link

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
        item = random.choice(items)
        item = item.fixed_height.url
    else:
        item = None
        if DEBUG:
            print ("""[dankBot] [DEBUG] search="{0}" resource="{1}" No results found.""").format(search, "giphy")
    return item


def google_search(search=""):
    service = googleapiclient.discovery.build("customsearch", "v1",
                                              developerKey=google_api_key)
    res = service.cse().list(
        q=str(search),
        cx=google_cseid,
        searchType="image",
        safe="high"
    ).execute()

    num_results = res[u'searchInformation'][u'totalResults']
    if num_results == 0:
        item = None
        if DEBUG:
                print ("""[dankBot] [DEBUG] search="{0}" resource="{1}" No results found.""").format(search, "google")
    else:
        # pprint.pprint(res)
        item = random.choice(res[u'items'])[u'link']

    return item


def dankify(words):
    """ /dankify message here! -> returns (m)(e)(s)(s)(a)(g)(e)(space)(h)(e)(r)(e)(bang) """
    dank = [ "(space)" if w == " " else "(bang)" if w == "!" else "({0})".format(w) for w in words ]
    dank = "".join(dank)
    return dank

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
    parsed = " ".join(parsed)

    # basic logic for multiple slash-commands
    if command == u'/dank':
        message = search_all(search=parsed)
    elif command == u'/dankify':
        message = dankify(parsed)
    elif command == u'/dankdev':
        message = devcmd.handler(parsed, who, state)
    elif command == u'/jank':
        message = giphy_search(search=parsed)
    elif command == u'/gank':
        message = google_search(search=parsed)
    elif command == u'/mank':
        message = imgur_search(search=parsed)
    elif command == u'/halp':
        message = "bro use /dank for all, /mank for imgur, /jank for giphy, /gank for goog"
    else:
        message = "welp! command not found: {0}".format(command)

    if who in state['HOTSEAT'] and random.randint(0, state['RNG']) == 0:
        message = "/me thinks @{0} needs to shut the f up...".format(who)

    resp = {"color":"random",
            "message": message,
            "notify": False,
            "message_format":"text"}
    # log-message
    print("""[dankBot] room="{0}" who="{1}" cmd="{2}" parsed="{3}" msg="{4}".""").format(room, who, command, parsed, message)

    return json.dumps(resp)


@app.route('/', method='GET')
def index():
    template = (
    "<html><body>"
    "dankBot for hipchat by @gelstudios<br>"
    "<br>"
    "The dankest bot in all the land.<br>"
    "Implements handlers: /dank for imgur, /jank for giphy, /gank for google, /halp for help<br>"
    "To install use this as the integration URL: <pre>http://imgur-hipchat.herokuapp.com/capabilities.json</pre><br>"
    "TODO: make api keys easier to manage, implement google_search() handler"
    "</body></html>")
    return template

if __name__=="__main__":
    port = os.environ.get('PORT', 8080)
    run(app, port=port, host='0.0.0.0')
