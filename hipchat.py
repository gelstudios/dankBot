#!/usr/bin/env python
# hipchat imgur bot

#/dankify message here -> returns (m)(e)(s)(s)(a)(g)(e) (h)(e)(r)(e)

from bottle import Bottle, run, get, post, request

from imgurpython import ImgurClient

import json

import os

def imgur_search(terms=""):
    imgur_id='3f07d3ccf3b7995'
    imgur_secret='076bb2967c9a1ffa013f443287b4a0f7d7eb76d7'

    client = ImgurClient(imgur_id, imgur_secret)

    items = client.gallery_search(terms, advanced=None, sort='time', window='all', page=0)
    # for i in items:
    #     print(i.link)
    if len(items) > 0:
        item = items[0].link
    else:
        item = u'i got nothing bro 💩'
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

    image = imgur_search(terms=" ".join(parsed))

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

#respond to post with a json message like:
#
# {
#     "color": "green",
#     "message": "It's going to be sunny tomorrow! (yey)",
#     "notify": false,
#     "message_format": "text"
# }
