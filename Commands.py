import socket,time

class BaseCommand:

	def __init__(self,id,command,channel,desc=""):
		self.id = id
		self.command = command
		self.args = []
		self.bot = None
		self.desc = (" - "+ desc if not desc == "" else "")
		self.channel = channel

	def reply(self,sender,args=""):
		pass

	def addArg(self,name,expl=""):
		self.args.append([name,(" - "+expl if not expl == "" else "")])

	def help(self):
		lines = []
		lines.append(self.command + self.desc)
		lines.append("Channel: "+self.channel)
		lines.append("Args: ")
		if len(self.args) == 1:
			lines[2] += self.args[0][0] + self.args[0][1]
		elif len(self.args) >= 2:
			lines[2] += self.args[0][0] + self.args[0][1]
			for arg in self.args[1:]:
				lines[2] += ", "+arg[0]+arg[1]
		return lines

class ShutdownCommand(BaseCommand):

	def __init__(self):
		BaseCommand.__init__(self,"shutdown","!shutdown","whisper")

	def reply(self, sender, args=""):
		if sender.lower() == "hydrox6":
			self.bot.whisper(sender, "Bye bye")
			self.bot.running = False
			self.bot.socket.shutdown(socket.SHUT_WR)
			self.bot.wsocket.shutdown(socket.SHUT_WR)
			print("Shutting Down")

class HelpCommand(BaseCommand):

	def __init__(self):
		BaseCommand.__init__(self,"help","!help","whisper","Provides a description and usage for a command.")
		self.addArg("command")

	def reply(self,sender,args=""):
		desire = args[1:].split(" ")[0]
		if desire == "":
			self.bot.whisper(sender,"Please provide a command to recieve help. Eg. !help help")
		else:
			found = []
			for k,v in self.bot.commands.items():
				if k[1:] == desire.lower():
					found.append(v)
			for k, v in self.bot.wcommands.items():
				if k[1:] == desire.lower():
					found.append(v)
			if len(found) == 0:
				self.bot.whisper(sender,"No commands found.")
			elif len(found) == 1:
				for l in found[0].help():
					self.bot.whisper(sender,l)
					time.sleep(0.3)
			else:
				self.bot.whisper(sender,"Found "+str(len(found))+" matches.")
				for x in range(0,len(found)):
					for l in found[x].help():
						self.bot.whisper(sender, l)
						time.sleep(0.1)