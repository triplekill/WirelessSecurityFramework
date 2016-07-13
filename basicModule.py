from __color import colorsNPrints as col
# must be called main
class main:


	def __init__(self):
		self.name = "basicModule" #same as the fileName
		
		self.cmds = [] # future stuff


		#Dictionaries with Options like: {"OptionName", [1/0, "Description", "<empty> for user input or default value"]}
		# 1/0 weather its a required option or not
		self.options = {
						"Option1":[1, "Description1", "default Value"],
						"Option1":[0, "Description2", ""]
						}



	def run(self):
		"""
			Needed to run the Module
		"""
		pass

	# to set the Options
	# could be left like that
	def setOption(self, key, value):
		for k, v in self.options.iteritems():
			if k == key:
				v[2] = value