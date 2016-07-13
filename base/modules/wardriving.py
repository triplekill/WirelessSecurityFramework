from __colors import colorsNPrints as col 
import subprocess 
import re 

# to supress Scapy warning level
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


from scapy.all import *
from scapy.all import *
import time
import threading

class main:

	def __init__(self):
		self.name = "wardriving"
		self.title = "Wardriving Module"
		self.description = "small module to use for wardriving"
		self.helpMsg = "Options: "
		self.helpMsg += "stuff stuff stuff"
	
		self.cmds = []#"run:r:exploit", "help:?:h", "show options:so"]
		self.options = {
						"Interface":[1, "Wlan Interface in monitor mode", "wlan0"],
						"Output":[0, "File to safe the wardriving output", ""]
						}
		

		# Module specific
		self.apList = {}
		self.stop = False
	
	def setOption(self, key, value):
		for k, v in self.options.iteritems():
			if k == key:
				v[2] = value

	def run(self, options=[]):
		print "\n" + col.writeUpdate("Checking Settings")
		iface = self.options["Interface"][2]

		if iface not in self.getInterfaces():
			print col.writeError("Interface is not valid")
			return -1

		elif not self.isMonitorMode(iface):
			print col.writeError("Interface is not in Monitor Mode")
			return -1
		conf.iface = iface

		print col.writeState(" Interface seems to be right (") + col.red(iface) + ")"

		print col.writeState("Capturing...\n")

		self.capture(iface)


	def capture(self, iface):

		print "\t    SSID" + " " *21 + "  BSSID" + " "*12 + "  Chnl.   Encr."
		print "\t    ----" + " " *21 + "  -----" + " "*12 + "  -----   ------"
		hopperThread = threading.Thread(target=self.channelHopper, args=(iface,))
		hopperThread.daemon = True
		hopperThread.start()

		try:
			sniffThread = threading.Thread(target=self.sniffIt, args=(iface,))
			sniffThread.daemon = True
			sniffThread.start()

			while sniffThread.isAlive():
				time.sleep(1)

		except KeyboardInterrupt:
			print "\n" + col.writeState("Closing Session..")
			self.stop = True
			time.sleep(.75)
			self.stop = False # for the next run
			self.saveOutput()


		except Exception as e:
			print e.message

	def sniffIt(self, iface):
		sniff(iface=iface, prn=self.pcktHandler, store=False,
      		lfilter=lambda p: (Dot11Beacon in p or Dot11ProbeResp in p), stop_filter=self.stopSniffing)

	def stopSniffing(self, x):
		if self.stop == True:
			return True
		return False

	def pcktHandler(self, pkt):
		
		bssid = pkt[Dot11].addr3
		if bssid in self.apList:
			return
		
		p = pkt[Dot11Elt]
		
		ssid, channel = None, None
		crypto = set()
		try:
		   	while isinstance(p, Dot11Elt):
		   		if p.ID == 0:
		   			ssid = p.info if '\x00' not in p.info and p.info != '' else '<Hidden SSID>'
		   			#ssid = p.info
		   			pass
		   		elif p.ID == 3:
		   			pass
		   			channel = ord(p.info)
				elif p.ID == 48:
					crypto.add("WPA2")
				elif p.ID == 221 and p.info.startswith('\x00P\xf2\x01\x01\x00'):
					crypto.add("WPA")
				p = p.payload
			if not crypto:
				if 'privacy' in cap:
					crypto.add("WEP")
				else:
					crypto.add("OPN")
		
			self.apList[bssid] = (ssid, channel, ' / '.join(crypto))
			if crypto == "OPN":
				crypto = col.green(" / ".join(crypto))
			else:
				crypto = col.red(" / ".join(crypto))
	   		print "\tAP: " + col.blue(ssid) + " " *(25-len(ssid)) + "| {0}".format(pkt.addr2) + " |  %i " %channel + " " * (2-len(str(channel))) + " | " + crypto
	

		except Exception as e:
			pass
			   	
	   	
	   	

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
		
	def saveOutput(self):

		print col.writeUpdate("Saving the Output..")
		tmp = False

		file = self.options["Output"][2]
		f = None
		try:
			if file == "":
				# safe tmp
				f = open("/tmp/sniffLog.xml", "w")
				tmp = True
			else:
				f = open(file.replace(".xml", "") + ".xml", "w")
			
			output = "<?xml version=\"1.0\"?>\n"
			output += "<accesspoints>\n"

			for key, val in self.apList.iteritems():
				output += "\t<ap>\n"
				output += "\t\t<bssid>{0}</bssid>\n".format(key)
				output += "\t\t<ssid>{0}</ssid>\n".format(val[0])
				output += "\t\t<channel>{0}</channel>\n".format(val[1])
				output += "\t\t<encryption>{0}</encryption>\n".format(val[2])
				output += "\t</ap>\n\n"
			
			
			output += "</accesspoints>\n"
			f.write(output)
			if tmp:
				print col.writeState("File safed under /tmp/sniffLog.xml")
			else:
				print col.writeState("File safed under {0}".format(file.replace(".xml", "") + ".xml"))

		except IOException:
			print col.writeError("Files could not be saved..")


	
	def printHelp(self):
		print "\t\nUsage:"
		print "\t" + self.helpMsg
		print

