import socket,re,time,os,importlib,pyclbr
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
		self.timer = 0
		self.wtimer = 0
		self.commands = {}
		self.wcommands = {}
		self.loadCommands()

	def loadCommands(self):
		import Commands
		cs = pyclbr.readmodule(Commands.__name__)
		del cs["BaseCommand"]
		for k,_ in cs.items():
			self.bindCommand(getattr(Commands,k)())


	def bindCommand(self,command):
		if command.channel == "whisper":
			self.wcommands[command.command] = command
		else:
			self.commands[command.command] = command
		command.bot = self

	def start(self):
		Thread(None,self.whisperListen,self.nick+"-Whispers",()).start()
		Thread(None,self.timerFunc,self.nick+"-timers",()).start()
		self.listen()

	def listen(self):
		incomplete = ""
		print("Starting chat watching")
		while self.running:
			try:
				last = self.socket.recv(128).decode("utf-8")						# Reads 128 Bytes from the chat
				recents = last.split("\r\n")										# Splits it up by line(s)
				recents[0] = incomplete + recents[0]								# Adds on the previous incomplete line.
				incomplete = recents[-1]											# Updates what line is considered incomplete.
				del recents[-1]													 	# Makes sure the incomplete line isn't processed this cycle.
				for oline in recents:											  	# Line format is :<sender>!<sender>@<sender>.tmi.twitch.tv PRIVMSG #<channel> :<message>
					sender = oline.split("!")[0][1:]								# Gets the sender.
					line = msg.sub("", oline)									  	# Gets the message using the wonders of Regex.
					if line[:19] == "PING :tmi.twitch.tv":							# Twitch sometimes sends these keep-alives. Sends the required response.
						self.socket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
					else:
						if not sender == self.nick:								 	# Makes IxiaBot ignore her own messages.
							if not oline[:14] == ":tmi.twitch.tv":					# Ignore automated messages from twitch when parsing commands and such.
								if not oline == u"":								# Ignore empty lines (this should be a rarity.
									if not oline == line:							# Turns out automated messages get filtered by this
										if self.timer == 0:
											if line[0] == "!":
												for c,r in self.commands.items():
													if line[:len(c)].lower() == c:
														r.reply(sender,line[len(c):])
										if "hello ixiabot" in line.lower() and sender.lower() == "hydrox6":  # For testing purposes only.
											self.chat("Hello Chat!")
										try:
											print(sender, "-", line)				# Prints the lines, so we can see what the bot sees.
										except UnicodeError:						# This may or may not be important, but it's there anyways.
											print("~~## ERROR LINE =( ##~~")
			except UnicodeDecodeError:
				print("ERROR: UnicodeDecodeError")
			time.sleep(0.01)													# Usually a good idea

	def whisperListen(self):
		incomplete = ""
		print("Starting whisper Thread")
		self.wsocket.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))	# Requests whispers. (Required)
		while self.running:													 	# This is technically the same code as above, just with the whisper socket.
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
								if not oline == line:  # Turns out automated messages get filtered by this
									if self.wtimer == 0:
										if line[0] == "!":
											for c, r in self.wcommands.items():
												if line[:len(c)].lower() == c:
													r.reply(sender, line[len(c):])
										elif "hello" in line:
											self.whisper(sender,"VoHiYo")
									try:
										print("#" + sender, "-", line)
									except UnicodeError:
										print("~~## ERROR LINE =( ##~~")
			time.sleep(0.01)


	def chat(self,message):
		self.socket.send("PRIVMSG #{} :{}\r\n".format(self.channel, message).encode("utf-8"))
		self.timer += 15

	def whisper(self,user,message):
		self.socket.send("PRIVMSG #{} :/w {} {}\r\n".format(self.channel, user, message).encode("utf-8"))
		self.wtimer += 15

	def timerFunc(self):
		while self.running:
			if self.timer < 0: self.timer = 0
			if self.timer > 0:
				self.timer -= 1
			if self.wtimer < 0: self.wtimer = 0
			if self.wtimer > 0:
				self.wtimer -= 1
			time.sleep(0.1)