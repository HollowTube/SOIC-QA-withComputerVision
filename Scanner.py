
import cv2	
from Analyser import Analyser
from ImageTaker import ImageTaker


class Scanner(object):

	def __init__(self,cam):
		self.cam = cam
		self.display = DisplayManager(cam)
		self.analyser = Analyser(cam)
	
		
	def fullScan(self):
		self.cam.captureBinarizePinsAndLettering()
		self.cam.cropOutPinZonesinBlackandWhite()
		self.cam.cropOutLetteringinBlackandWhite()

		binaryLetters = self.cam.binaryLetters
		binaryPin = self.cam.binaryPin
		topBin = self.cam.topPinRow
		botBin = self.cam.botPinRow

		if  self.analyser.checkFlip() is False:
			print("No chip detected or flipped chip")
			print("Test result: FAILED")
			#self.displayDebug(zone = "Missing")
			return False
	
		if self.analyser.checkOutOfTray() is False:
			print("Chip out of Tray")
			print("Test result: FAILED")
			#self.displayDebug(zone = "Out of Tray")
			return False
		
		if self.checkPin(topBin,botBin) is False:
			print("Test result: FAILED")
			return False
		
		print("Test result: PASSED")
		print("----------------")
		print
		#self.displayDebug()
		return True

	def checkPin(self):
		topPins = self.cam.topPinRow
		botPins = self.cam.botPinRow

		cornersTop = self.analyser.topCornersUsingContour(topPins)
		cornersTop = self.analyser.getTop20(cornersTop)
		if cornersTop is []:
			print("Top pins missing")
			#self.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.botCornersUsingContour(botPins)
		cornersBot = self.getBot20(cornersBot)
		if cornersBot is []:
			print("Bot pins missing")
			#self.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			#self.displayDebug(zone = "Top Pins")
			return False

		if self.analyser.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			#self.displayDebug(zone = "Bot Pins")
			return False

		if self.analyser.checkSpacing(cornersTop) is False:
			print("Top spacing off")
			#self.displayDebug(zone = "Top Pins")
			return False
		if self.analyser.checkSpacing(cornersBot) is False:
			print("Bot spacing off")
			#self.displayDebug(zone = "Bot Pins")
			return False
		return True