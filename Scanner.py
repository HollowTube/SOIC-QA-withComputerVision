import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2	
from Analyser import Analyser
from ImageTaker import ImageTaker
from DisplayManager import DisplayManager



class Scanner(object):

	def __init__(self,cam):
		self.cam = cam
		self.display = DisplayManager(cam)
		self.analyser = Analyser(cam)
	
	def fullScan(self):
		self.currentSet = self.cam.getNewImageSet()

		centerLettering = self.currentSet['centerLetteringBin']
		URPin = self.currentSet['URPinBin']
		BLPin = self.currentSet['BLPinBin']

		pinsBot = self.currentSet['centerLetteringBin']
		pinsTop = self.currentSet['centerLetteringBin']

		if  self.analyser.checkFlip(centerLettering) is False:
			print("No chip detected or flipped chip")
			print("Test result: FAILED")
			self.display.displayDebug(zone = "Missing")
			return False
		if self.analyser.checkOutOfTray(URPin,BLPin) is False:
			print("Chip out of Tray")
			print("Test result: FAILED")
			self.display.displayDebug(zone = "Out of Tray")
			return False
		try:
			if self.checkPin(pinsTop,pinsBot) is False:
				print("Test result: FAILED")
				return False
		except:
			
			print("Unexpected Error")
			print("Test result: FAILED")
			return False
			
		print("Test result: PASSED")
		print("----------------")
		print
		return True

	def checkPin(self,topPins,botPins):
		cornersTop = self.analyser.getHighestCorners(topPins)
		if cornersTop is []:
			print("Top pins missing")
			self.display.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.analyser.getLowestCorners(botPins)
		if cornersBot is []:
			print("Bot pins missing")
			self.display.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			self.display.displayDebug(zone = "Top Pins")
			return False

		if self.analyser.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			self.display.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkSpacing(cornersTop) is False:
			print("Top spacing off")
			self.display.displayDebug(zone = "Top Pins")
			return False
		if self.analyser.checkSpacing(cornersBot) is False:
			print("Bot spacing off")
			self.display.displayDebug(zone = "Bot Pins")
			return False
		return True

if __name__ == "__main__":
	cam = ImageTaker()
	scanner = Scanner(cam)
	while True:
		currentSet = cam.getNewImageSet()
		scanner.display.displayDebugInformation()
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			if scanner.fullScan() is False:
				cv2.waitKey(0)
		


		
