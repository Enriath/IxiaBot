import socket,re,time,datetime,json,urllib
import TwitchUtils,IxiaExceptions

msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

class IxiaBot:

    def __init__(self,channel,nick,token):
        self.nick = nick
        self.token = token
        self.channel = channel
        self.socket = TwitchUtils.connectToChannel(self.token, self.nick, self.channel)

    def listen(self):
        incomplete = ""
        while True:
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
                    if not oline[:14] == ":tmi.twitch.tv" and not oline == u"" and not line == oline:
                        if "greetings" in line:
                            self.chat("ohaider")
                        try:
                            print(sender, "-", line)
                        except UnicodeError:
                            print("~~## ERROR LINE =( ##~~")
    def chat(self,message):
        self.socket.send("PRIVMSG #{} :{}\r\n".format(self.channel, message).encode("utf-8"))