import os
import random
import time

import redis
import json

import hipchat

redis_connection = redis.StrictRedis(host=os.environ.get("REDIS_HOST"),
                                     port=os.environ.get("REDIS_PORT", 63790),
                                     password=os.environ.get("REDIS_AUTH"))

quips = {
    "already_dead": ["{0} is already dead but {1} wants to make sure.",
                     "{0} died and {1} is still killing him!"],
    "killed": ["{0} murdered {1} in the face!",
               "{0} brought the hammer down on {1}!"],
    "damaged": ["{0} attacked {1} for {2} damage",
                "{0} diddled {1} for {2} diddly-damage"],
    "blocked": ["{0} blocked {1}'s attack.", ],
    "blocking": ["{0} takes a blocking stance.",
                 "{0} readies himself for an attack."],
    "no_target": ["{0} flails wildly at the air and hits himself in the face.",
                  "{0} doesn't know whats going on, sets himself on fire."],
    "rez": ["{0} starts coming back to life!", "Is a pheonix rising from the ashes."],
    "rezzing": ["{0} is still scraping his entrails together.", "{0} is still remembering how to be alive."],
    "dead": ["{0} is dead and cannot do anything.", ],
    "stupid": ["{0} went insane and decided to stab himself.", "{0} is a moron and attacked himself!"],
    "not the time": ["now is not the time to use that", ],
}

MEME_SEARCH = {
    "block": "blocking",
    "damage": "attacking",
    "kill": "murdered",
    "rez": "ressurect",
    "stupid": "stupid",

}


class Player(object):
    def __init__(self, player_data):

        if not player_data:
            raise ValueError("tried to construct player with null data")
        self.id = player_data.get("id")
        self.name = player_data.get("name")
        self.hp = player_data.get("hp")
        self.attack = player_data.get("attack")
        self.defense = player_data.get("defense")
        self.status = player_data.get("status")
        self.last_action = player_data.get("last_action")
        self.max_hp = player_data.get("max_hp")

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return json.dumps(self.__dict__)


def get_quip(quip):
    if not quip:
        return "pro quip"
    quip_list = quips.get(quip)
    ret = quip_list[random.randint(0, len(quip_list)-1)]
    return ret


# create a new player object with default values
def create_new_player(player_id, name):
    noob = {
        "name": name,
        "id": player_id,
        "hp": 100,
        "attack": 20,
        "defense": 5,
        "max_hp": 100,
        "status": "alive",
        "last_action": time.time()
    }
    return Player(noob)


# Look in redis for player
def get_player(who_id):
    data = redis_connection.hgetall(who_id)
    if data:
        # return json.loads(data)
        return Player(data)
    else:
        return None


def save_player(player):
    player.last_action = time.time()
    redis_connection.hmset(player.id, player.__dict__)


def handler(cmd, cmd_args, dank_json):

    who_id = dank_json[u'item'][u'message'][u'from'][u'id']
    # who = dank_json[u'item'][u'message'][u'from'][u'mention_name']
    who = dank_json[u'item'][u'message'][u'from'][u'name']

    print "[dankBot] Battle: {0} USR: {1}".format(repr(cmd), who_id)

    # check for player
    player = get_player(who_id)

    # if no player, make new one
    if not player:
        player = create_new_player(who_id, who)
        save_player(player)

    if cmd == "/status":
        return repr(player)

    if player.status == "dead":
        if cmd == "/rez":
            return rez(player)
        else:
            return get_quip("dead").format(player.name)
    elif player.status == "rezzing":
        if (time.time() - float(player.last_action)) < 30.0:
            return get_quip("rezzing").format(player.name)
        else:
            player.status = "alive"
            player.hp = player.max_hp
            save_player(player)

    if cmd == "/attack":
        mentions = dank_json[u'item'][u'message'][u'mentions']
        return attack(player, cmd_args.split(), mentions)
    elif cmd == "/block":
        return block(player)
    elif cmd == "/rez":
        return get_quip("not the time").format()
    else:
        return "herp derp"


def attack(player, args, mentions):
    if not args or not mentions:
        response = get_quip("no_target").format(player.name)
        return response

    if len(mentions) > 1 and len(args) > 1:
        response = "too many targets"
    else:
        target = get_player(mentions[0].get("id"))
        if not target:
            target = create_new_player(mentions[0].get("id"), mentions[0].get("name"))

        # Check for dead target
        if target.status == "dead":
            response = get_quip("already_dead").format(target.name, player.name)
            return response

        # Check for blocking
        if target.status == "blocking":
            response = get_quip("blocked").format(target.name, player.name)
            target.status = "alive"
            save_player(target)
            return response

        # Compare hp values
        if (int(target.hp) - int(player.attack)) <= 0:
            target.status = "dead"
            target.hp = 0
        # do the attack
        else:
            target.hp = int(target.hp) - int(player.attack)

        save_player(target)
        if target.status == "dead":
            response = get_quip("killed").format(player.name, target.name)
            response += os.linesep + hipchat.search_all(MEME_SEARCH.get("kill"))
        else:
            if player.name == target.name:
                response = get_quip("stupid").format(player.name)
                response += os.linesep + hipchat.search_all(MEME_SEARCH.get("stupid"))
            else:
                response = get_quip("damaged").format(player.name, target.name, target.attack)
                response += os.linesep + hipchat.search_all(MEME_SEARCH.get("damage"))
    return response


def block(player):
    player.status = "blocking"
    save_player(player)
    response = get_quip("blocking").format(player.name)
    response += os.linesep + hipchat.search_all(MEME_SEARCH.get("block"))
    return response


def rez(player):
    player.status = "rezzing"
    save_player(player)
    response = get_quip("rez").format(player.name)
    response += os.linesep + hipchat.search_all(MEME_SEARCH.get("block"))
    return response
