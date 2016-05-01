[![Build Status](https://travis-ci.org/gelstudios/dankBot.svg?branch=master)](https://travis-ci.org/gelstudios/dankBot) <- but don't trust this badge just yet (see issue #23)

# wat?
- The _dankest_ chat bot in all the land, currently returns image searches from:
  - imgur
  - giphy
  - ~~google images~~
- Can also perform these amazing feats of bot-ness:
  - Roll dice
  - Choose an item from a list, for the indicisive bot user
  - Play cards against humanity(!)
  - Play a crappy battle game
  - Be sassy AF

# how?
- hipchat webhooks + python + magic
- runs on heroku or anywhere you want to run python

# why?
- because we could

# setup
- if you don't have the python virtualenv package, install it: `pip install virtualenv`
- clone + go into dankBot repo directory: `git clone https://github.com/gelstudios/dankBot && cd dankBot`
- create a virtual env inside the dankbot repo: `virtualenv venv`
- load virtual env: `source venv/bin/activate`
- setup your environment by editing `dankbot.env.dist`, save it as `dankbot.env`
  - imgur_id='your_imgur_client_id' # <- imgur key goes here
  - imgur_secret='your_imgur_client_secret' # <- imgur secret goes here
  - google_api_key='your_google_api_key' # <- google api key goes here
  - google_cseid='your_google_cseid' # <- google cseid goes here
  - DEBUG=True # <- controls debug console logging (default is False)
  - NOMEME=True # <- controls meme search during battle function
  - AUTH_TOKEN='your_hipchat_auth_token' # <- dankbot needs its own hipchat auth token for CaH DM's
  - REDIS_HOST='localhost' # <- change this if not using a local redis instance
  - REDIS_PORT=63790 # <- redis port number
  - REDIS_AUTH='your_redis_auth_string' # <- redis password goes here

- load the env file: `source dankbot.env`
- start the bot: `python hipchat.py`
- in another shell, run the tests: `./test.sh`

# who?
- lovingly crafted these fine folks:
  - @gelstudios
  - @emenym
  - @arichards611
  - @jrg4017

# todo
- [Fix open issues](https://github.com/gelstudios/dankBot/issues)
- Create a driver interface for different chat service providers
- Slack driver for above interface
- a basic REST api (maybe)
