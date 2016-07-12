import socket,re,time,datetime,json,urllib
from threading import Thread
import TwitchUtils,IxiaExceptions

msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
whisper = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv WHISPER \w+ :")

class IxiaBot:

    def __init__(self,channel,nick,token):
        self.nick = nick
        self.token = token
        self.channel = channel
        self.socket = TwitchUtils.connectToChannel(self.token, self.nick, self.channel)
        self.wsocket = TwitchUtils.setupWhispers(self.token,self.nick)
        self.running = True

    def start(self):
        Thread(None,self.whisperListen,self.nick+"-Whispers",()).start()
        self.listen()

    def listen(self):
        incomplete = ""
        while self.running:
            last = self.socket.recv(128).decode("utf-8") # Reads 128 Bytes from the chat
            recents = last.split("\r\n") # Splits it up by line(s)
            recents[0] = incomplete + recents[0] # Adds on the previous incomplete line.
            incomplete = recents[-1] # makes incomplete the new incomplete line
            del recents[-1] # Makes sure the incomplete line isn't processed this cycle
            for oline in recents:
                #Line format is :<sender>!<sender>@<sender>.tmi.twitch.tv PRIVMSG #<channel> :<message>
                sender = oline.split("!")[0][1:] # gets the sender
                line = msg.sub("", oline) # Gets the message using the wonders of Regex
                if line[:19] == "PING :tmi.twitch.tv":
                    self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                else:
                    if not sender == self.nick and not oline[:14] == ":tmi.twitch.tv" and not oline == u"" and not line == oline:
                        if "greetings" in line:
                            self.chat("ohaider")
                        try:
                            print(sender, "-", line)
                        except UnicodeError:
                            print("~~## ERROR LINE =( ##~~")
        time.sleep(0.01)

    def whisperListen(self):
        incomplete = ""
        print("Starting whisper Thread\n")
        self.wsocket.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
        running = True
        while running:
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
                    if not oline[:14] == ":tmi.twitch.tv" and not oline == u"" and not line == oline:
                        if line[0:9] == "!shutdown":
                            self.whisper(sender,"Bye bye")
                            self.running = False
                            running = False
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
        self.socket.send("PRIVMSG #{} :/w {} {}\r\n".format(self.channel, user,message).encode("utf-8"))