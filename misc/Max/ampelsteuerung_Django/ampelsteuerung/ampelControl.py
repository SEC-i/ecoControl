import os



def switchOn(color):
	os.system("ssh pi@172.16.19.114 \"sudo sispmctl -o %s\""%color)


def switchOff(color):
	os.system("ssh pi@172.16.19.114 \"sudo sispmctl -f %s\""%color)


def status(color):
	if color == "green":
		numColor = 2
	else:
		numColor = 1

	output = os.popen("ssh pi@172.16.19.114 \"sudo sispmctl -q -n -g " + str(numColor) + "\"").read()
	print color, output

	return output