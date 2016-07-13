from scapy.all import *
from __color import colorsNPrints as col
import threading
import time

# must be called main
class main:


	def __init__(self):
		self.name = "ssidToBssid" #same as the fileName
		
		self.cmds = [] # future stuff


		#Dictionaries with Options like: {"OptionName", [1/0, "Description", "<empty> for user input or default value"]}
		# 1/0 weather its a required option or not
		self.options = {
						"Interface":[1, "Interface in Monitor Mode", "wlan0"],
						"SSID":[1, "SSID of the Router", ""],
						"waittime":[0, "Waiting time until bssid is found (in ms)", "500"]
						}


		self.found = False
		self.bssid = ""
		self.stop = True

	def run(self):
		"""
			Needed to run the Module
		"""
		iface = self.options["Interface"][2]

		if iface not in self.getInterfaces():
			print col.writeError("Interface is not valid")
			return -1

		elif not self.isMonitorMode(iface):
			print col.writeError("Interface is not in Monitor Mode")
			return -1
		conf.iface = iface



	def getBssid(self):
		"""
			Sniff the Wlan traffic for a few seconds to find the right ssid/bssid
		"""
		
		time = self.options["waittime"][2]

		# Start Channel Hopping
		chnlHopper = threading.Thread(target=self.channelHopper, args=(iface, ))
		chnlHopper.daemon = True
		chnlHopper.start()

		# start the sniffing
		sniffThread = threading.Thread(target=self.sniff, args=(iface, ))
		sniffThread.daemon = True
		sniffThread.start()

		for i in range(round(time/10)):
			if self.found:
				col.printState("The Bssid of {0} is: {1}".format(self.options["SSID"][2], self.bssid))
				self.stop = True
				break
			time.sleep(0.1)


		self.stop = True



	def sniff(self, iface):
		sniff(iface=iface, prn=self.pcktHandler, store=False,
		      		lfilter=lambda p: (Dot11Beacon in p or Dot11ProbeResp in p), stop_filter=self.stopSniffing)

	def stopSniffing(self, x):
		if self.stop == True:
			return True
		return False



	def pcktHandler(self, p):

		bssid = pkt[Dot11].addr3


		if bssid.lower() != self.bssid.lower():
			return

		p = pkt[Dot11Elt]
		ssid = None

		try:
		   	while isinstance(p, Dot11Elt):
		   		if p.ID == 0:
		   			ssid = p.info if '\x00' not in p.info and p.info != '' else '<Hidden SSID>'
		 except:
		 	pass

		 self.found = True
		 self.ssid = ssid



	def channelHopper(self, iface):
	
		waitTime = 1 # in seconds
		i = 1
		while True:
			try:
				subprocess.Popen(['iw', 'dev', iface, 'set', 'channel', str(i)])
			except:
				pass
			i = (i + 1) % 13 + 1
			time.sleep(waitTime)

	def getInterfaces(self):
		"""
			get the interfaces from "ifconfig" with regex and return them in a list
		"""
		output = subprocess.Popen('ifconfig', stdout=subprocess.PIPE).communicate()[0]
		interfaces = [f.replace(": ","") for f in re.findall("^[a-zA-Z0-9]+: ", output, re.MULTILINE)]
		return interfaces


	# to set the Options
	# could be left like that
	def setOption(self, key, value):
		for k, v in self.options.iteritems():
			if k == key:
				v[2] = value