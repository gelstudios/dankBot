import os
import redis
import json
import requests
import random
import unicodedata
import string

LOCAL_DEBUG = os.environ.get("LOCAL_DEBUG")

if LOCAL_DEBUG:
    AUTH_TOKEN = os.getenv("DEBUG_AUTH_TOKEN")
else:
    AUTH_TOKEN = os.getenv("DANKBOT_AUTH_TOKEN")

REDIS_DATA_KEY = "cards_db"

redis_connection = redis.StrictRedis(host=os.environ.get("REDIS_HOST"),
                                     port=os.environ.get("REDIS_PORT", 63790),
                                     password=os.environ.get("REDIS_AUTH"))

cards_data = json.loads(redis_connection.get(REDIS_DATA_KEY))

HELP_STRING = "/cards newgame - start a new game of cah\n" \
              "/cards join - join a game\n" \
              "/cards start - start the game once everyone has joined\n" \
              "/cards play <card number> - play a card from your hand\n" \
              "/cards choose <card number> - choose the winning card[s]\n" \
              "/cards next - start the next round of play \n" \
              "/cards waiting - who are we waiting to take a turn?\n" \
              "/cards leave - leave a game in progress\n"


# example game object layout
card_game = {"players": {"player1": {"score": 0,
                                     "name": "player1name",
                                     "hand": {"card1id": "card1", "card2id": "card2"}},
                         "player2": {"score": 0,
                                     "name": "player1name",
                                     "hand": {"card1id": "card1", "card2id": "card2"}},
                         "player3": {"score": 0,
                                     "name": "player1name",
                                     "hand": {"card1id": "card1", "card2id": "card2"}},
                         },
             "round": 0,
             "score_cap": 10,
             "rounds": {1: {"win_cards": {"blackcard": "blackcardid", "whitecards": ["whitecards"]},
                            "turn_taken": []},
                        2: {"win_cards": {"blackcard": "blackcardid", "whitecards": ["whitecards"]},
                            "turn_taken": []},
                        },
             "czar": {"id": 'player1id', "name": 'player1'},
             "czar_list": [1234, 5342, 4113],
             "black_card": -1,
             "round_cards":  {"userid": 11234, "cards": ["card1", "card2"]},
             "cards_played": {"black": [1, 2, 3],
                              "white": [12, 34, 56]}
             }


class Game(object):
    def __init__(self, game_data):
        if not game_data:
            raise ValueError("tried to construct player with null data")

        self.players = game_data.get("players")
        self.round = game_data.get("round")
        self.score_cap = game_data.get("score_cap")
        self.hand_size = game_data.get("hand_size")
        self.rounds = game_data.get("rounds")
        self.black_card = game_data.get("black_card")
        self.czar = game_data.get("czar")
        self.czar_list = game_data.get("czar_list")
        self.round_cards = game_data.get("round_cards")
        self.cards_played = game_data.get("cards_played")

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return json.dumps(self.__dict__)


def cards_handler(cmd, cmd_args, dank_json):
    who_id = dank_json[u'item'][u'message'][u'from'][u'id']
    who_name = dank_json[u'item'][u'message'][u'from'][u'name']
    roomid = dank_json[u'item'][u'room'][u'id']

    if cmd_args == "newgame":
        game, message = create_new_game(who_id, who_name, roomid)
        if game:
            save_game(game, roomid)
        return message

    elif cmd_args == "join":
        return player_join_game(who_id, who_name, roomid)
    elif cmd_args == "start":
        return start_game(roomid)
    elif cmd_args == "next":
        return start_round(None, roomid)
    elif "play" in cmd_args:
        return play_cards(cmd_args, who_id, who_name, roomid)
    elif "choose" in cmd_args:
        return choose(cmd_args, who_id, roomid)
    elif "waiting" in cmd_args:
        return waiting_on(roomid)
    elif "leave" in cmd_args:
        return leave_game(roomid, who_id, who_name)
    elif "halp" in cmd_args:
        return HELP_STRING
    elif "help" in cmd_args:
        return HELP_STRING
    elif "die" in cmd_args:
        return "No."
    else:
        return "/cards help"


def leave_game(roomid, whoid, who_name):
    game = get_game(roomid)
    if not game:
        message = "There is no game. \"/cards newgame\" to start"
        return message

    if str(whoid) not in game.players.keys():
        return "You are not in this game."
    czar_left = False
    if whoid == game.czar.get("id"):
            czar_left = True
            # return start_round(None, roomid)
            # return "The card czar cannot leave during their round!"

    del game.players[str(whoid)]

    if len(game.players) <= 1:
        ret = "Everyone has left. Ending the game."
        end_game(game, roomid)
        return ret
    elif czar_left:
        ret = "The czar has left the game. Moving to next round. " + start_round(game, roomid)
    else:
        ret = "{who} has left the game.".format(who=who_name)

    save_game(game, roomid)
    return ret


def end_game(game, roomid):
    del_game(game, roomid)


def waiting_on(roomid):
    game = get_game(roomid)
    if not game:
        message = "There is no game. \"/cards newgame\" to start"
        return message
    have_played = game.rounds.get(str(game.round)).get("turn_taken")
    all_players = game.players.keys()
    waiting = []
    for playerid in all_players:
        if int(playerid) not in have_played:
            if int(playerid) != game.czar.get("id"):
                waiting.append(game.players.get(playerid).get("name"))

    ret = "Waiting on "
    if not waiting:
        ret += "{czar} to choose a card.".format(czar=game.czar.get("name"))
    else:
        for person in waiting:
            ret += person
            ret += " "
    return ret


def play_cards(cards, who_id, who_name, roomid):
    game = get_game(roomid)
    if not game:
        return "There is no game. \"/cards newgame\" to start"
    if who_id == game.czar.get("id"):
        if LOCAL_DEBUG:
            # allow this for testing and debugging
            pass
        else:
            return "The card czar cannot play his own round!"

    already_played = game.rounds.get(str(game.round)).get("turn_taken")
    if who_id in already_played:
        return "{who} has already played a card this round.".format(who=who_name)

    who_string = str(who_id)
    if str(who_string) not in game.players:
        return "You are not in this game. Wait for the next one!"

    card_list = cards.split()[1:]
    if not card_list:
        return "You forgot to specify a card to play."

    pick_number = cards_data.get("blackCards")[game.black_card].get("pick")
    if len(card_list) < pick_number:
        return "You must play {pickno} card(s).".format(pickno=pick_number)

    for card in card_list:
        if card not in game.players.get(who_string)["hand"]:
            return "Invalid selection of cards. Try again."

    submit_list = []
    for card in card_list:
        card_id = game.players.get(who_string)["hand"].get(card)

        submit_list.append(card_id)
        replace_card(card, game, who_string)

    game.round_cards[str(len(game.round_cards)+1)] = {"userid": who_id,
                                                    "cards": submit_list}

    send_cards(who_id, game.players.get(who_string)["hand"])

    game.rounds.get(str(game.round)).get("turn_taken").append(who_id)
    already_played = game.rounds.get(str(game.round)).get("turn_taken")

    message = "{who} played their card.".format(who=who_name)

    if len(already_played) >= len(game.players)-1:
        message += "\nEveryone has played a card."
        message += "\nTime to pick a winner!\n\n"

        message += send_candidates(game)

    save_game(game, roomid)
    return message


def choose(card, who_id, roomid):
    message = ""
    game = get_game(roomid)
    if who_id != game.czar.get("id"):
        return "Only the card czar can choose a winner."
    if game.round <= 0:
        return "The game has not started."
    if game.rounds[str(game.round)].get("win_cards").get("blackcard") >= 0:
        return "This round is over."
    chosen_card = card.split()[1:][0]
    if not chosen_card:
        return "You must choose a winner"

    already_played = game.rounds.get(str(game.round)).get("turn_taken")
    if len(already_played) < len(game.players)-1:
        return "\nPlease wait for all players to play a card..."
    else:
        try:
            winner_name = game.players.get((str(game.round_cards.get(chosen_card).get("userid")))).get("name")
        except AttributeError as ae:
            return "Could not find card. Did the player leave?"
        game.players.get((str(game.round_cards.get(chosen_card).get("userid"))))["score"] += 1
        line = get_winning_text(game, chosen_card)

        message = "The winner of this round is {name} with:\n {card}\n".format(name=winner_name, card=line)
        game.rounds[str(game.round)].get("win_cards")["blackcard"] = game.black_card

        for whitecard in game.round_cards.get(chosen_card).get("cards"):
            game.rounds[str(game.round)].get("win_cards")["whitecards"].append(whitecard)

        winner_score = game.players.get((str(game.round_cards.get(chosen_card).get("userid")))).get("score")
        if winner_score >= game.score_cap:
            message += "{who} has reached {scorecap} points and wins the game!\n".format(who=winner_name, scorecap=game.score_cap)
            end_game(game, roomid)

        save_game(game, roomid)
        return message


def get_winning_text(game, winner_id):
    return get_cards_text(game, winner_id)


def get_losing_text(game, winner_id):
    losers = []
    for key, value in game.round_cards.items():
        if key not in [winner_id]:
            print(value)
            losers.append(key)

    losers_text = ""
    for loser in losers:
        losers_text += get_cards_text(game, loser)
        losers_text += "\n"
    return losers_text


def get_all_cards_text(game):
    all_cards_text = ""
    for someone in game.round_cards.keys():
        all_cards_text += "{num}: {text}".format(num=someone, text=get_cards_text(game, someone))
        all_cards_text += " \n"
    return all_cards_text


def get_cards_text(game, user_id):
    cards_text = ""
    black_card_text = get_black_card_contents(game.black_card).get("text")
    for card in game.round_cards.get(user_id).get("cards"):
        current_card_text = get_white_card_contents(card)
        cards_text += current_card_text
        if black_card_text.count("_") < 1:
            black_card_text += " " + current_card_text
        else:
            black_card_text = string.replace(black_card_text, "_", current_card_text, 1)
    line = "{cards_text}".format(cards_text=black_card_text)
    return line


def replace_card(card, game, who_id):
    try:
        game.players.get(who_id)["hand"][card] = get_white_card(game)
    except IndexError as ie:
        print(ie.message)


def create_new_game(who_id, who_name, roomid):
    game = get_game(roomid)
    if not game:
        new_game = create_game(who_id=who_id, who_name=who_name)
        return new_game, "{who} has wants to play Cards Against Humanity! \"/cards join\" to join the game.".format(who=who_name)
    elif game.score_cap < 0:
        new_game = create_game(who_id=who_id, who_name=who_name)
        return new_game, "{who} has wants to play Cards Against Humanity! \"/cards join\" to join the game.".format(who=who_name)
    else:
        return None, "A game is already in progress"


def create_game(who_id, who_name):
    new_game_setup = {
        "players": {who_id: {"score": 0, "name": who_name, "hand": {}}},
        "round": 0,
        "score_cap": 10,
        "rounds": {},
        "hand_size": 10,
        "black_card": -1,
        "czar": {"id": who_id, "name": who_name},
        "czar_list": [who_id],
        "round_cards": {},
        "cards_played": {"black": [], "white": []}
    }
    return Game(new_game_setup)


def player_join_game(who_id, who_name, roomid):
    game = get_game(roomid)
    if not game:
        message = "There is no game to join. \"/cards newgame\" to start"
        return message
    elif str(who_id) in game.players.keys():
        message = "You have already joined this game."
        return message
    else:
        game.players[who_id] = {"score": 0, "name": who_name, "hand": {}}
        game.czar_list.append(who_id)
        save_game(game, roomid)
        message = "{who} has joined the game.".format(who=who_name)
        return message


def start_game(roomid):
    game = get_game(roomid)
    if not game:
        message = "There is no game to start. \"/cards newgame\" to start"
        return message
    elif game.round > 0:
        message = "The games has already been started."
    else:
        # game.round = 1
        # game.round = next_round(game)
        give_start_cards(game)
        message = start_round(game, roomid)
    return message


def start_round(game, roomid):
    if not game:
        game = get_game(roomid)
    try:
        if game.score_cap < 0:
            return "The game has ended. Start a new one."
    except AttributeError as ae:
        return "There is no game."

    if game.black_card > 0:
        if game.rounds[str(game.round)].get("win_cards").get("blackcard") < 0:
            return "This round is still going."

    if game.round >= 1:
        game.czar = next_czar(game)

    game.round = next_round(game)
    black_card = get_black_card(game)
    game.black_card = black_card
    game.cards_played["black"].append(black_card)
    black_card_contents = get_black_card_contents(black_card)

    message = "{who} is the card czar.\n\n {card}\nPick {pick}.".format(who=game.czar.get("name"), card=black_card_contents['text'], pick=black_card_contents['pick'])
    save_game(game, roomid)
    return message


def next_czar(game):
    current_czar_id = game.czar.get("id")
    try:
        new_czar_id = game.czar_list[game.czar_list.index(current_czar_id)+1]
    except IndexError as ie:
        new_czar_id = game.czar_list[0]

    new_czar = {"id": int(new_czar_id), "name": game.players.get(str(new_czar_id)).get("name")}
    return new_czar


def next_round(game):
    game.round_cards = {}
    round_next = game.round + 1
    game.rounds[round_next] = {"win_cards": {"blackcard": -1, "whitecards": []},
                            "turn_taken": []}
    return round_next


def give_start_cards(game):
    players = game.players
    for player in players:
        for num in range(0, game.hand_size):
            white_card = get_white_card(game)
            game.cards_played["white"].append(white_card)
            game.players.get(player)["hand"][num] = white_card
        send_cards(player, game.players.get(player)["hand"])


def send_candidates(game):
    message = get_all_cards_text(game)
    return message


def send_cards(who_id, cards):
    fleeb = format_white_cards(cards)

    resp = []
    for c in fleeb.items():
        resp.append("{0} : {1}".format(*c))

    resp = '\n'.join(sorted(resp))

    data = {'message': resp}
    data_string = json.dumps(data)

    headers = {"Content-Type": "application/json"}
    # debug
    if LOCAL_DEBUG:
        who_id = 2110189
    url = "https://api.hipchat.com/v2/user/{whoid}/message?auth_token={auth}".format(whoid=who_id, auth=AUTH_TOKEN)
    r = requests.post(
        url=url,
        data=data_string,
        headers=headers)
    if LOCAL_DEBUG:
        print(r.content)


def format_white_cards(cards):
    hand = {}
    for hand_index, card_index in cards.items():
        hand[hand_index] = unicodedata.normalize('NFKD', get_white_card_contents(card_index)).encode('ascii', 'ignore')
    return hand


def get_black_card_contents(card):
    card_contents = cards_data[u'blackCards'][card]
    return card_contents


def get_white_card_contents(card):
    try:
        card_contents = cards_data[u'whiteCards'][int(card)]
    except IndexError as ie:
        card_contents = ie.message
        print(ie.message)
    except TypeError as te:
        print(te.message)
        card_contents = te.message
    return card_contents


def get_black_card(game):
    black_cards = cards_data[u'blackCards']

    card_choice = cards_data[u'blackCards'].index(random.choice(black_cards))
    while card_choice in game.cards_played["black"]:
        card_choice = cards_data[u'blackCards'].index(random.choice(black_cards))

    return card_choice


def get_white_card(game):
    cards_played = game.cards_played
    white_cards = cards_data[u'whiteCards']

    card_choice = cards_data[u'whiteCards'].index(random.choice(white_cards))
    while card_choice in game.cards_played["white"]:
        card_choice = cards_data[u'whiteCards'].index(random.choice(white_cards))

    return card_choice


def get_card_data():
    data = redis_connection.get(REDIS_DATA_KEY)
    return json.loads(data)


def get_game(roomid):
    game_name = "card_game." + str(roomid)
    data = redis_connection.get(game_name)
    if data:
        mer = json.loads(data, "ascii")
        ret = Game(mer)
        return ret
    else:
        return None


def save_game(game, roomid):
    game_name = "card_game." + str(roomid)
    redis_connection.set(game_name, json.dumps(game.__dict__).encode("utf8"))


def del_game(game, roomid):
    game_name = "card_game." + str(roomid)
    redis_connection.delete(game_name)
