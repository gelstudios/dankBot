#!/usr/bin/env python
# hipchat imgur bot

#/dankify message here -> returns (m)(e)(s)(s)(a)(g)(e) (h)(e)(r)(e)

from bottle import Bottle, run, get, post, request

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

import json

import os

imgur_id = os.environ.get('imgur_id', None)
imgur_secret = os.environ.get('imgur_secret', None)

def imgur_search(search=""):
    try:
        client = ImgurClient(imgur_id, imgur_secret)
    except ImgurClientError as e:
        if e.status_code == 503:
            return u'can i haz valid api keys?'
        else:
            return u'sorry i could not reach imgur :/  E_MSG: {0} E_CODE: {1}'.format(e.error_message, e.status_code)
    try:
        items = client.gallery_search(search, advanced=None, sort='time', window='all', page=0)
    except ImgurClientError as e:
        return u'derp, something bad happened: {0}'.format(e.error_message)

    # for i in items:
    #     print(i.link)
    if len(items) > 0:
        item = items[0].link
    else:
        item = u'i got nothing for "{0}", bro'.format(search)
    return item

    # print "tag search"
    # items = client.gallery_tag("datto", sort='viral', page=0, window='week')
    # print dir(items.items[0])

app = Bottle()

@app.route('/', method='POST')
def handle():
    derp = request.json
    msg = derp[u'item'][u'message'][u'message']

    m = msg.split()

    command = m[0]
    parsed = m[1:]

    if parsed[0] == 'debug':
        pass

    image = imgur_search(search=" ".join(parsed))

    resp = {"color":"random",
            "message": image,
            "notify": False,
            "message_format":"text"}

    return json.dumps(resp)

@app.route('/', method='GET')
def index():
    return "ImgurBot by @gelstudios, add a slash command handler to your chat room and set the URL to this one"

if __name__=="__main__":
    port = os.environ.get('PORT', 8080)
    run(app, port=port, host='0.0.0.0')
