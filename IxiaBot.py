import socket,re,time
from threading import Thread
import TwitchUtils

msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
whisper = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv WHISPER \w+ :")


class IxiaBot:

    def __init__(self,channel,nick,token):
        self.nick = nick
        self.token = token
        self.channel = channel
        self.socket = TwitchUtils.connectToChannel(self.token, self.nick, self.channel)
        self.wsocket = TwitchUtils.setupWhispers(self.token, self.nick)
        self.running = True

    def start(self):
        Thread(None,self.whisperListen,self.nick+"-Whispers",()).start()
        self.listen()

    def listen(self):
        incomplete = ""
        print("Starting chat watching")
        while self.running:
            last = self.socket.recv(128).decode("utf-8")                        # Reads 128 Bytes from the chat
            recents = last.split("\r\n")                                        # Splits it up by line(s)
            recents[0] = incomplete + recents[0]                                # Adds on the previous incomplete line.
            incomplete = recents[-1]                                            # Updates what line is considered incomplete.
            del recents[-1]                                                     # Makes sure the incomplete line isn't processed this cycle.
            for oline in recents:                                               # Line format is :<sender>!<sender>@<sender>.tmi.twitch.tv PRIVMSG #<channel> :<message>
                sender = oline.split("!")[0][1:]                                # Gets the sender.
                line = msg.sub("", oline)                                       # Gets the message using the wonders of Regex.
                if line[:19] == "PING :tmi.twitch.tv":                          # Twitch sometimes sends these keep-alives. Sends the required response.
                    self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                else:
                    if not sender == self.nick:                                 # Makes IxiaBot ignore her own messages.
                        if not oline[:14] == ":tmi.twitch.tv":                  # Ignore automated messages from twitch when parsing commands and such.
                            if not oline == u"":                                # Ignore empty lines (this should be a rarity.
                                if not line == oline:                           # I'm not sure why this line is here, as this code is from an older project.
                                    if "greetings" in line:                     # For testing purposes only.
                                        self.chat("ohaider")
                                    try:
                                        print(sender, "-", line)                # Prints the lines, so we can see what the bot sees.
                                    except UnicodeError:                        # This may or may not be important, but it's there anyways.
                                        print("~~## ERROR LINE =( ##~~")
        time.sleep(0.01)                                                        # Usually a good idea

    def whisperListen(self):
        incomplete = ""
        print("Starting whisper Thread")
        self.wsocket.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))    # Requests whispers. (Required)
        while self.running:                                                     # This is technically the same code as above, just with the whisper socket.
            last = self.wsocket.recv(128).decode("utf-8")
            recents = last.split("\r\n")
            recents[0] = incomplete + recents[0]
            incomplete = recents[-1]
            del recents[-1]
            for oline in recents:
                sender = oline.split("!")[0][1:]
                line = whisper.sub("", oline)
                if line[:19] == "PING :tmi.twitch.tv":
                    self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                else:
                    if not sender == self.nick:
                        if not oline[:14] == ":tmi.twitch.tv":
                            if not oline == u"":
                                if not line == oline:
                                    if line[0:9] == "!shutdown":
                                        self.whisper(sender,"Bye bye")
                                        self.running = False
                                        self.socket.shutdown(socket.SHUT_WR)
                                        self.wsocket.shutdown(socket.SHUT_WR)
                                        print("Shutting Down")
                                    elif "hola" in line:
                                        self.whisper(sender,"te amo")
                                    try:
                                        print("#" + sender, "-", line)
                                    except UnicodeError:
                                        print("~~## ERROR LINE =( ##~~")
            time.sleep(0.01)


    def chat(self,message):
        self.socket.send("PRIVMSG #{} :{}\r\n".format(self.channel, message).encode("utf-8"))

    def whisper(self,user,message):
        self.socket.send("PRIVMSG #{} :/w {} {}\r\n".format(self.channel, user, message).encode("utf-8"))