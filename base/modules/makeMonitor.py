from __colors import colorsNPrints as col 
import subprocess
import re

# must be called main
class main:


	def __init__(self):
		self.name = "makeMonitor" #same as the fileName
		
		self.cmds = []

		self.options = {
						"Interface":[1, "Wireless Interface to put in monitor mode", "wlan0"],
						"Mode":[1, "0=disable, 1=enable", "1"]

						}


	def run(self):
		"""
			Needed to run the Module
		"""
		if not self.checkInterface():
			return

		if self.options["Mode"][2] == "1":
			self.Monitor()

		elif self.options["Mode"][2] == "0":
			self.Monitor(False)

		else:
			print col.writeError("Wrong Mode")


	def Monitor(self, enable=True):

		iface = self.options["Interface"][2]

		# Interface Down for procesing
		downOP = subprocess.Popen(('ifconfig %s down' % iface).split(), stdout=subprocess.PIPE).communicate()[0]
		# Enable/Disable Monitor
		if enable:	
			iwConfigOP = subprocess.Popen(('iwconfig %s Mode Monitor' %iface).split(), stdout=subprocess.PIPE).communicate()[0]
		else:
			iwConfigOP = subprocess.Popen(('iwconfig %s Mode Managed' %iface).split(), stdout=subprocess.PIPE).communicate()[0]
		
		#bring Interface back up again
		upOP = subprocess.Popen(('ifconfig %s up' % iface).split(), stdout=subprocess.PIPE).communicate()[0]
		

		if "Operation not supported" in iwConfigOP:
			if enabled:
				print col.writeError("Could not enable Monitor Mode")
			else:
				print col.writeError("Could not disable Monitor Mode")
			return
		if enable:
			print col.writeState("Enabled Monitor mode on %s" % iface)
		else:
			print col.writeState("Disabled Monitor mode on %s" % iface)

	

	def checkInterface(self):
		"""
			get the interfaces from "ifconfig" with regex and return them in a list
		"""
		output = subprocess.Popen('ifconfig', stdout=subprocess.PIPE).communicate()[0]
		interfaces = [f.replace(": ","") for f in re.findall("^[a-zA-Z0-9]+: ", output, re.MULTILINE)]
		
		if self.options["Interface"][2] in interfaces:
			print col.writeState("Interface seems to be valid")
			return True
		print scol.writeError("Interface is not valid")
		return False

	def setOption(self, key, value):
		for k, v in self.options.iteritems():
			if k == key:
				v[2] = value