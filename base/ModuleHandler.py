import os
import readline
from itertools import chain
from modules.__colors import colorsNPrints as col

import sys

class ModuleHandler:

	
	def __init__(self):
		# Set Autocompletion
		readline.set_completer(self.completer)
		readline.parse_and_bind("tab: complete")
	
		# Module Options
		self.crntModule = ""
		self.isModuleSet = False
		self.modCommands = ["set ", "show ", "options", "run", "exploit", "r", "exit", "close"]
		
		#debugging options
		self.debug = 1
		self.allModules = self.showModules()

		# Tab Completion
		self.showTab = False


	def header(self):
		#print "***********************************"
		#print "*   Wireless Security Framework   *"
		#print "***********************************"

		banner = """
 _    _ _ _____            ______                                           _    
| |  | (_/  ___|           |  ___|                                         | |   
| |  | |_\ `--.  ___  ___  | |_ _ __ __ _ _ __ ___   _____      _____  _ __| | __
| |/\| | |`--. \/ _ \/ __| |  _| '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |/ /
\  /\  | /\__/ |  __| (__  | | | | | (_| | | | | | |  __/\ V  V | (_) | |  |   < 
 \/  \/|_\____/ \___|\___| \_| |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_|\_\ """
		print col.green(banner)
		print "\n\t| Author: HansMartin"
		print "\t| Modules: " + str(len(self.allModules)) + "\n"



	def mainLoop(self):
		# endless loop for the user inputs
		self.header()		

		while 1:

			try:
				_input = raw_input(col.underlined("wisif") + " > ")
				self.inputHandler(_input)
			
			except KeyboardInterrupt:
				self.clearConsole();
				exit(1)

	def inputHandler(self, inp):
		""" 
			Will discribe what to do on user input
		"""


		if inp == "":
			pass
		elif inp == "exit" or inp == "close":
			exit(1)
		elif  inp == "list" or inp == "ls" or inp == "show modules":
			""" 
				Show the Module list
			"""

			print "\nModules:"
			print "-"*8
			for mod in self.showModules():
				print "\t* " + mod

			print 

		elif inp.startswith("use "):
			""" 
				use a Module
			"""
			moduleName = inp.replace("use ", "")
			if self.checkModule(moduleName):
				#print "\n[+] loading Module..."
				
				self.loadModule(moduleName)
				print 
		
		# command not recognized
		elif inp == "clear":
			self.clearConsole()
		else:
			print col.writeError("Command not recognized")



	def showModules(self):
		return [f.replace(".py", "") for f in os.listdir(os.getcwd() + "/base/modules") if not f.startswith("__") and not f.endswith(".pyc")]


	def checkModule(self, mod):
		mods = self.showModules()
		if mod in mods:
			return True
		return False
	
	
	def loadModule(self, mod):
		try:
			_temp = __import__("modules." + mod, globals(), locals(), [mod], -1) 
			self.isModuleSet = True
		except Exception as e:
			if self.debug == 1:
				print e
				return -1
			print col.writeError("Import module Error")
		

		""" 
			New Module Main Loop
		"""
		module = _temp.main()
		self.moduleLoop(mod, module)
		
		


	def moduleLoop(self, modName, modLib):
		"""
			Loop through modules commands
		"""
		cmds = modLib.cmds
		cmds = list(chain.from_iterable([f.split(":") for f in modLib.cmds]))
		self.modCommands += cmds
		self.modCommands += [f[0] + " " for f in modLib.options.items()]

		while True:
			try:
				inp = raw_input(col.underlined("wisif") + " module(" + col.red(modName) + ") > ")
				retVal = self.modInputHandler(inp, modLib, cmds)
				if retVal == -1:
					self.isModuleSet = False
					self.crntModule = ""
					break

			except KeyboardInterrupt:
				self.clearConsole();
				exit(1)


	def modInputHandler(self, inp, modLib, cmds):
		
		if inp == "":
			pass
		elif inp == "exit" or inp == "close":
			return -1

		elif inp == "show options":
			"""	
				Show the Options for the Module (taken from the options Field in the Mod. Class)
			"""
			options = modLib.options
			longest = max([(len(f[0]), f[0]) for f in options.items()])[1]
			
			print "\nModule Options (modules/" + modLib.name + "):\n"
			print "\tName" + " " * (len(longest)- 2) + "Current Setting  Required  Description"
   			print "\t----" + " " * (len(longest)- 2) + "---------------  --------  -----------"
   		
   			for key, val in options.iteritems():
   				requ = "yes" if val[0] == 1 else "no"
   				optionSet = val[2]
				if val[2] == "":
					print "\t" + key + " " * (len(longest) + 2 - len(key)+17) + requ + " " * (10-len(requ)) + val[1]
				else:
					print "\t" + key + " " * (len(longest) + 2 - len(key)) + val[2] + " " * (17-len(val[2])) + requ + " " * (10-len(requ)) + val[1]
			print 

		elif inp.startswith("set "):
			"""
				set the options for the Module
			"""
			setted = False

			for key, val in modLib.options.iteritems():
				if key == inp.split(" ")[1]:
					modLib.setOption(key, inp.split(" ")[2])
					setted = True

			if not setted:
				print col.writeError("Option not available")

		
		elif inp == "run" or inp == "r" or inp == "exploit":
			"""
				Run the Exploit/Module
			"""
			print col.writeState("Running Module")
			modLib.run()

		elif inp == "clear":
			"""
				Clear the Console
			"""
			self.clearConsole()
		else:
			"""
				Unknown command 
			"""
			print col.writeError("Command not recognized")

	def clearConsole(self):
    		os.system("clear")

	def clearModuleCache(self):
    		self.isModuleSet = False
    		self.crntModule = ""

    


	def completer(self, text, state):
		bCmds = ["help", "use ", "list", "show ", "modules", "version", "exit", "close"]
		bCmds += self.showModules()
		sCmds = ["show ", "options", "set "]

		if self.isModuleSet:
			options = [x for x in self.modCommands if x.startswith(text)]

  		else:
  			options = [x for x in bCmds if x.startswith(text)]

  		try:
        		return options[state]
    		except IndexError:
        		return None


    