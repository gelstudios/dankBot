import requests
import json

import hipchat
from hipchat_notification import text_image_card_notification, send_room_post_response


def strip_see_word(def_string):
    try:
        index = def_string.index('\r\n\r\nSee [word]')
    except ValueError:
        return def_string
    else:
        return def_string[:index]


def format_definitions(definition, example):
    definition = strip_see_word(definition)

    html = definition + '\n\nExample: ' + example
    return html


def parse_response_definitions(json_string):
    parsed_json = json.loads(json_string)

    definitions = []

    if parsed_json['list']:
        for item in parsed_json['list']:
            temp = format_definitions(item['definition'], item['example'])
            definitions.append(temp)

    return definitions


def get_definitions(word):
    url = "http://api.urbandictionary.com/v0/define?term=%s" % \
          word

    r = requests.get(url=url)

    return parse_response_definitions(r.text)


def total_definitions(define, room_id):
    definitions = get_definitions(define)

    # sends individual cards via post
    for definition in definitions:
        url = hipchat.search_all(search=define)
        json_str = text_image_card_notification(message=definition, word=define, image_url=url)
        send_room_post_response(data=json_str, room_id=room_id)

    if len(definitions) > 0:
        return str(len(definitions)) + ' total definition(s) found for ' + define

    return ''
