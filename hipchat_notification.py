import requests
import json
import os

LOCAL_DEBUG = os.environ.get("LOCAL_DEBUG")

if LOCAL_DEBUG:
    AUTH_TOKEN = os.getenv("DEBUG_AUTH_TOKEN")
else:
    AUTH_TOKEN = os.getenv("DANKBOT_AUTH_TOKEN")


def text_image_card_notification(message, word, image_url, link_url=None):
    if link_url:
        url = link_url
    else:
        url = image_url

    return {
        "message": message,
        "message_format": "html",
        "notify": False,
        "card": {
            "style": "link",
            "url": url,
            "id": "c253adc6-11fa-4941-ae26-7180d67e814a",
            "title": word,
            "format": "medium",
            "description": message,
            "date": 1453867674631,
            "thumbnail": {
                "url": image_url,
                "url@2x": image_url,
                "width": 1193,
                "height": 564
            }
        }
    }


def text_notification(message):
    return {"color": "random",
            "message": message,
            "notify": False,
            "message_format": "text"}


def send_room_post_response(room_id, data):
    data_string = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    if LOCAL_DEBUG:
        room_id = 2747855
        # this is the void room

    url = "https://api.hipchat.com/v2/user/{who}/message?auth_token={auth}".format(who=room_id, auth=AUTH_TOKEN)
    r = requests.post(
        url=url,
        data=data_string,
        headers=headers)

    if LOCAL_DEBUG:
        print(r.content)

# testing for image card
# curl -d '{"message_format": "html", "notify": false, "card": {"thumbnail": {"url": "http://i.imgur.com/nlWEZ8V.gif", "width": 1193, "url@2x": "http://i.imgur.com/nlWEZ8V.gif", "height": 564}, "id": "c253adc6-11fa-4941-ae26-7180d67e814a", "style": "link", "url": "http://i.imgur.com/nlWEZ8V.gif", "description": "The removal of excess body hair via waxing, shaving, plucking. Also manscap - ing, ed\n\n<b>When your chick calls you a Yeti, it might be time for a little manscaping.</b>", "format": "medium", "title": "manscape", "date": 1453867674631}, "message": "The removal of excess body hair via waxing, shaving, plucking. Also manscap - ing, ed\n\n<i>When your chick calls you a Yeti, it might be time for a little manscaping.</i>"}' -H 'Content-Type: application/json' https://datto.hipchat.com/v2/room/2881488/notification?auth_token=86yRUjEIki86eKNRRveM7g4L6RERf19gh8QGmJ81
#


#https://datto.hipchat.com/v2/room/2747855/notification?auth_token=JxTyQ8L2ee0PqI0pNHNGvlntbpUHAeThxanG6yYM