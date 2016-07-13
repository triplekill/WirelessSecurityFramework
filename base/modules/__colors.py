class colorsNPrints:
    
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    """
        Colors
    """

    @staticmethod
    def underlined(text):
    	return colorsNPrints.UNDERLINE + text + colorsNPrints.ENDC
    @staticmethod
    def red(text):
    	return colorsNPrints.RED + text + colorsNPrints.ENDC
    @staticmethod
    def blue(text):
    	return colorsNPrints.BLUE + text + colorsNPrints.ENDC
    @staticmethod
    def green(text):
    	return colorsNPrints.GREEN + text + colorsNPrints.ENDC


    """
        Print the Error/Update and Statements
    """

    @staticmethod
    def writeError(text):
        return colorsNPrints.red("[-]") + " " + text

    @staticmethod
    def writeUpdate(text):
        return colorsNPrints.blue("[*]") + " " + text

    @staticmethod
    def writeState(text):
        return colorsNPrints.green("[+]") + " " + text