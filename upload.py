import os
import redis

redis_connection = redis.StrictRedis(host=os.environ.get("REDIS_HOST"),
                                     port=os.environ.get("REDIS_PORT", 63790),
                                     password=os.environ.get("REDIS_AUTH"))

FILE = "cah.json"
REDIS_KEY = "cards_db"


def main():
    cards = redis_connection.get("cards_db")
    if cards:
        clear()
    data = get_data(FILE)
    upload(data)


def get_data(targetfile):
    f = open(targetfile, "r")
    data = f.read()
    return data


def clear():
    redis_connection.delete(REDIS_KEY)


def upload(data):
    redis_connection.set(REDIS_KEY, data)

if __name__ == "__main__":
    main()