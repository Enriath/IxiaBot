import socket
import IxiaExceptions
def connectToChannel(token,nick,channel):
    s = socket.socket()
    s.connect(("irc.twitch.tv",6667))

    s.send("PASS {}\r\n".format(token).encode("utf-8"))
    s.send("NICK {}\r\n".format(nick).encode("utf-8"))
    s.send("JOIN {}\r\n".format("#"+channel).encode("utf-8"))
    r = s.recv(35+len(nick)).decode("utf-8")
    if r[-14:] == u'Welcome, GLHF!':
        return s
    else:
        raise IxiaExceptions.CannotConnectException(r)
