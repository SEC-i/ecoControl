import os
import time


def switchOn(color):
	color=numColor(color)
	os.system("ssh pi@172.16.19.114 \"sudo sispmctl -o %s\""%color)


def switchOff(color):
	color=numColor(color)
	os.system("ssh pi@172.16.19.114 \"sudo sispmctl -f %s\""%color)


def status(color):
	numColor = numColor(color)
	output = os.popen("ssh pi@172.16.19.114 \"sudo sispmctl -q -n -g " + str(numColor) + "\"").read()
	print color, output

	return output

def numColor(color):
	if color == "green":
		return 2
	else:
		return 1


def morseShort():
	switchOn("red")
	time.sleep(0.5)
	switchOff("red")


def morseLong():
	switchOn("red")
	time.sleep(1.5)
	switchOff("red")