import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2	
import time
from Analyser import Analyser
from ImageTaker import ImageTaker
from DisplayManager import DisplayManager


class Scanner(object):

	def __init__(self,cam):
		self.cam = cam
		self.display = DisplayManager(cam)
		self.analyser = Analyser(cam)
		self.debug = True
		self.currentSet = self.cam.getNewImageSet()
		cv2.imshow('Main',self.cam.raw)
		cv2.moveWindow('Main',0,0)
		if self.debug is True:
			cv2.imshow('Marking',self.cam.binaryLettering)
			cv2.moveWindow('Marking',500,0)
		cv2.waitKey(1)

	def fullScan(self):
		self.currentSet = self.cam.getNewImageSet()
		for x in range (0,3):
			cv2.imshow('Main', self.cam.raw)
			cv2.waitKey(1)
		if self.debug is True:
			cv2.imshow('Marking',self.cam.binaryLettering)
			cv2.moveWindow('Marking',500,0)
		#else:
		#	self.display.displayRaw()


		centerLettering = self.currentSet['centerLetteringBin']
		URPin = self.currentSet['URPinBin']
		BLPin = self.currentSet['BLPinBin']

		if  self.analyser.checkFlip(centerLettering) is False:
			print("Marker not found")
			#self.display.displayDebug(zone = "Missing")
			return False
		if self.analyser.checkOutOfTray(URPin,BLPin) is False:
			print("Sprocket empty")
			#print("Test result: FAILED")
			#self.display.displayDebug(zone = "Out of Tray")
			return False
		try:
			if self.checkPin() is False:
				#print("Test result: FAILED")
				return False
		except:
			print("Unexpected Error")
			#print("Test result: FAILED")
			return False
			
		#print("Test result: PASSED")
		#print("----------------")
		#print
		return True

	def checkPin(self):

		botPins = self.currentSet['botPinRowBin']
		topPins = self.currentSet['topPinRowBin']

		cornersTop = self.analyser.getHighestCorners(topPins)
		if len(cornersTop) != 20:
			print("Top pins missing")
			print len(cornersTop)
			#self.display.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.analyser.getLowestCorners(botPins)
		if len(cornerBot) !=20:
			print("Bot pins missing")
			#self.display.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			#self.display.displayDebug(zone = "Top Pins")
			return False

		if self.analyser.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			#self.display.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkSpacing(cornersTop) is False:
			print("Top spacing off")
			#self.display.displayDebug(zone = "Top Pins")
			return False
		if self.analyser.checkSpacing(cornersBot) is False:
			print("Bot spacing off")
			#self.display.displayDebug(zone = "Bot Pins")
			return False
		return True

if __name__ == "__main__":
	cam = ImageTaker()
	scanner = Scanner(cam)
	while True:
		currentSet = cam.getNewImageSet()
		scanner.display.displayDebugInformation()
		scanner.fullScan()
		time.sleep(1)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			if scanner.fullScan() is False:
				cv2.waitKey(0)
		


		
