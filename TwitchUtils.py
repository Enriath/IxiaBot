import socket,json
from urllib.request import urlopen
import IxiaExceptions


def connectToChannel(token,nick,channel,server=("irc.twitch.tv",6667)):
    s = socket.socket()
    s.connect(server)

    s.send("PASS {}\r\n".format(token).encode("utf-8"))
    s.send("NICK {}\r\n".format(nick).encode("utf-8"))
    s.send("JOIN {}\r\n".format("#"+channel).encode("utf-8"))
    r = s.recv(35+len(nick)).decode("utf-8")
    if r[-14:] == u'Welcome, GLHF!':
        return s
    else:
        raise IxiaExceptions.CannotConnectException(r)


def setupWhispers(token,nick):
    u = urlopen("http://chatdepot.twitch.tv/room_memberships?oauth_token={}".format(token[6:])).read()
    j = json.loads(u.decode("utf-8"))
    j = j["memberships"][0]
    cname = j["room"]["irc_channel"]
    servers = j["room"]["servers"]
    aserver = ""
    for server in servers:
        server = server.split(":")
        if server[1] == "6667":
            try:
                ws = connectToChannel(token,nick,cname,(server[0], 6667))
            except IxiaExceptions.CannotConnectException:pass
            else:
                print("Connected to whisper Channel")
                return ws
    for server in servers:
        server = s.split(":")
        if server[1] == "80":
            try:
                ws = connectToChannel(server[0], 80, cname)
            except IxiaExceptions.CannotConnectException:
                pass
            else:
                print("Connected to whisper Channel")
                return ws
    return None