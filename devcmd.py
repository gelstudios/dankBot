import os

authorized = ['eromano','MichaelEmeny','RyanPineau','Charlie', 'JulieGabler']

def hotseat(p, state):
    if p:
        if p[0] == "add" and len(p) > 1:
            if p[1]:
                state['HOTSEAT'].append(p[1])
        elif p[0] == "rm" and len(state['HOTSEAT']) > 0:
            _ = state['HOTSEAT'].pop()
    r = 'hotseat: ' + " ".join(state['HOTSEAT'])
    return r

def rng(p, state):
    if p:
        if p[0].isdigit():
            state['RNG'] = int(p[0])
    r = "rng: {0}".format(state['RNG'])
    return r

def handler(commands, who, state):
    print "[dankBot] DEV: {0} USR: {1}".format(repr(commands), who)

    commands = commands.split()
    cmd = commands[0]
    if len(commands) > 1:
        p = commands[1:]
    else:
        p = None

    if who in authorized:
        if cmd == 'hotseat':
            r = hotseat(p, state)
        elif cmd == 'rng':
            r = rng(p, state)
        elif cmd == 'status':
            r = "[dev] " + repr(os.environ)
        elif cmd == 'shell':
            r = eval(" ".join(p))
        else:
            r = "what is thy bidding, my master?"
    else:
        r = "dev mode: up up down down left right left right a b start"
    return r
