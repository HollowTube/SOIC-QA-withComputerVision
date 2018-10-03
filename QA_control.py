import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2	
import time
from ImageAnalyse import Analyser
from ImageCapture import ImageCapture
from DisplayManager import DisplayManager
import numpy as np

class QA_control(object):

	def __init__(self,cam):
		self.cam = cam
		self.display = DisplayManager(cam)
		self.analyser = Analyser(cam)
		self.debug = False
		self.currentSet = self.cam.getNewImageSet()
		self.pinfail=0;
		cv2.imshow('Main',self.cam.raw)
		cv2.moveWindow('Main',0,0)
		#if self.debug is True:
		#	cv2.imshow('BW',self.cam.binaryPin)
		#	cv2.moveWindow('BW',500,0)
		cv2.waitKey(1)

	def fullScan(self):
		# Start with full image capture
		self.currentSet = self.cam.getNewImageSet()
		for x in range (0,3):
			cv2.imshow('Main', self.cam.raw)
			cv2.waitKey(1)

		centerLettering = self.currentSet['centerLetteringBin']
		URPin = self.currentSet['URPinBin']
		BLPin = self.currentSet['BLPinBin']


		# First check if the device exist in sprocket
		if self.analyser.checkOutOfTray(URPin,BLPin) is False:
			print("Sprocket empty")
			#print("Test result: FAILED")
			#self.display.displayDebug(zone = "Out of Tray")
			return False

		if  self.analyser.checkFlip(centerLettering) is False:
			print("Marker not found")
			return False

		# The capture new image with device and rotation
		try:		
			self.currentSet = self.cam.getExtImageSet()
		except Exception as e:
			print("Unexpected Error")
			print(str(e))
			#print("Test result: FAILED")
			return True
		#for x in range (0,3):
		#	cv2.imshow('Ext', self.cam.raw)
		#	cv2.waitKey(1)

		TopRowPin=self.currentSet['topPinRowBin']
		BotRowPin=self.currentSet['botPinRowBin']
		if self.debug is True:
			cv2.imshow('Marker',centerLettering)
			cv2.imshow('Top pin',TopRowPin)
			cv2.imshow('Bottom pin',BotRowPin)
			cv2.imshow('BW',self.cam.binaryPin)
			cv2.moveWindow('Marker',600,0)
			cv2.moveWindow('Top pin',0,500)
			cv2.moveWindow('Bottom pin',0,600)
			cv2.waitKey(1)
		try:
			if self.checkPin() is False:
				self.pinfail=self.pinfail+1
				return True
		except Exception as e:
			print("Unexpected Error")
			print(str(e))
			return True

		return True

	def checkPin(self):

		botPins = self.currentSet['botPinRowBin']
		topPins = self.currentSet['topPinRowBin']

		cornersTop = self.analyser.getHighestCorners(topPins)
		print len(cornersTop)
		if len(cornersTop) != 20:
			print("Top pins missing")
			print len(cornersTop)
			#self.display.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.analyser.getLowestCorners(botPins)
		print len(cornersBot)
		if len(cornersBot) !=20:
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
	cam = ImageCapture()
	scanner = QA_control(cam)
	while True:
		currentSet = cam.getExtImageSet()
		
		#BotPinSet=scanner.currentSet['botPinRowBin']
		#TopPinSet=scanner.currentSet['topPinRowBin']
		#TopPinSet = np.uint8(TopPinSet)
		#BotPinSet = np.uint8(BotPinSet)
		#tbox=scanner.analyser.findContourBoxes(TopPinSet)
		#bbox=scanner.analyser.findContourBoxes(BotPinSet)
		#for box in tbox:
		#	cv2.drawContours(scanner.cam.raw,[box],0,(0,128,255),2)
		#for box in bbox:
		#	cv2.drawContours(scanner.cam.raw,[box],0,(0,128,255),2)
		#cv2.imshow('TPR',scanner.cam.raw)
		#cv2.waitKey(1)
		start_time = time.time()
		if scanner.fullScan() is True:
			print ("Pass")
		end_time = time.time()
		print("time taken {0}".format(end_time-start_time))
		time.sleep(1)
	foo.cap.stream.release()
	cv2.destroyAllWindows()	


		
