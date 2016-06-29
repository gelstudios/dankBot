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
    headers = {"Content-Type": "application/json"}

    if LOCAL_DEBUG:
        # this is the void room
        room_id = 2747855

    url = "https://api.hipchat.com/v2/room/{who}/message?auth_token={auth}".format(who=room_id, auth=AUTH_TOKEN)
    print(url)
    r = requests.post(
        url=url,
        data=json.dumps(data),
        headers=headers
    )

    if LOCAL_DEBUG:
        print(r.content)


# testing for image card formatting:
# curl -d '{"message_format": "html", "notify": false, "card": {"thumbnail": {"url": "http://i.imgur.com/nlWEZ8V.gif", "width": 1193, "url@2x": "http://i.imgur.com/nlWEZ8V.gif", "height": 564}, "id": "c253adc6-11fa-4941-ae26-7180d67e814a", "style": "link", "url": "http://i.imgur.com/nlWEZ8V.gif", "description": "The removal of excess body hair via waxing, shaving, plucking. Also manscap - ing, ed\n\n<b>When your chick calls you a Yeti, it might be time for a little manscaping.</b>", "format": "medium", "title": "manscape", "date": 1453867674631}, "message": "The removal of excess body hair via waxing, shaving, plucking. Also manscap - ing, ed\n\n<i>When your chick calls you a Yeti, it might be time for a little manscaping.</i>"}' -H 'Content-Type: application/json' https://datto.hipchat.com/v2/room/2881488/notification?auth_token=77UPpEL65DHDr4qO11eX4fXCduLdMQ4QqMxftUFW
