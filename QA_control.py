import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2	
import time
from ImageAnalyse import Analyser
from ImageCapture import ImageCapture
from DisplayManager import DisplayManager
import numpy as np
import matplotlib.pyplot as plt

class QA_control(object):

	def __init__(self,cam):
		self.cam = cam
		self.display = DisplayManager(cam)
		self.analyser = Analyser(cam)
		self.debug = False
		self.currentSet = self.cam.getExtImageSet()
		self.error_code=0

		cv2.imshow('Main',self.cam.raw)
		cv2.moveWindow('Main',0,50)
		cv2.waitKey(500)

	def fullScan(self):
		# The capture new image with device and rotation
		try:		
			self.currentSet = self.cam.getExtImageSet()
		except Exception as e:
			#print("Unexpected Error")
			self.error_code=1
			return False		
		cv2.imshow('Main', self.cam.raw)
		
		cv2.waitKey(5)

		centerLettering = self.currentSet['centerLetteringBin']
		URPin = self.currentSet['URPinBin']
		BLPin = self.currentSet['BLPinBin']

		TopRowPin=self.currentSet['topPinRowBin']
		BotRowPin=self.currentSet['botPinRowBin']
		if self.debug is True:
			cv2.imshow('Marker',centerLettering)
			cv2.imshow('Top pin',URPin)
			cv2.imshow('Bottom pin',BLPin)
			cv2.imshow('BW',self.cam.binaryPin)
			cv2.moveWindow('Marker',500,0)
			cv2.moveWindow('Top pin',0,500)
			cv2.moveWindow('Bottom pin',0,600)
			cv2.waitKey(10)

		# First check if the device exist in sprocket
		if self.analyser.checkOutOfTray(URPin,BLPin) is False:
			#print("Sprocket empty")
			self.error_code=1
			self.ErrorDisplay(1,0)
			return False

		if  self.analyser.checkFlip(centerLettering) is False:
			#print("Marker not found")
			self.error_code=2
			self.ErrorDisplay(2,0)
			return False
		pin=0
		botPins = self.currentSet['botPinRowBin']
		topPins = self.currentSet['topPinRowBin']
		try:
			cornersTop = self.analyser.getHighestCorners(topPins)
			cornersBot = self.analyser.getLowestCorners(botPins)
		except Exception as e:
			#print("Unexpected Error")
			#print(str(e))
			self.error_code=9
			self.ErrorDisplay(3,0)
			return False

		if len(cornersTop) != 20:
			#print("Fail to detect Top pins",len(cornersTop))
			self.error_code=3
			self.ErrorDisplay(3,pin)
			return False
		if len(cornersBot) !=20:
			#print("Fail to detect Bot pins",len(cornersBot))
			self.error_code=4
			self.ErrorDisplay(4,pin)
			return False
		check_status,pin=self.analyser.checkLinearity(cornersTop)
		if  check_status is False:
			#print("Top pins not aligned")
			self.error_code=5
			self.ErrorDisplay(5,pin)
			return False
		check_status,pin=self.analyser.checkLinearity(cornersBot)
		if check_status is False:
			#print("Bot pins not aligned")
			self.error_code=6
			self.ErrorDisplay(6,pin)
			return False
		check_status,pin=self.analyser.checkSpacing(cornersTop)
		if  check_status is False:
			#print("Top spacing off")
			self.error_code=7
			self.ErrorDisplay(7,pin)
			return False
		check_status,pin=self.analyser.checkSpacing(cornersBot)
		if  check_status is False:
			#print("Bot spacing off")
			self.error_code=8
			self.ErrorDisplay(8,pin)
			return False

		self.error_code=0
		return True

	def ErrorDisplay(self,error,pin):
		temp=cv2.cvtColor(self.cam.gray,cv2.COLOR_GRAY2RGB)
		if error ==2:
			self.drawErrorRectangleOverROI(self.cam.centerLetteringZone ,temp)
		elif error ==3 or error==4:
			tbox=self.analyser.findContourBoxes(self.cam.binaryPin)
			for box in tbox:
				cv2.drawContours(temp,[box],0,(0,0,255),2)
		elif error ==5:
			cv2.rectangle(temp, ((pin-1)*47,5) , (pin*47,25) , (0,0,255) , 2)
		elif error ==7:
			cv2.rectangle(temp, ((pin-1)*47+10,25) , (pin*47+10,70) , (0,0,255) , 2)
		elif error ==6:
			cv2.rectangle(temp, ((pin-1)*47,self.cam.yDSize-25) , (pin*47,self.cam.yDSize-5) , (0,0,255) , 2)
		elif error ==8:
			cv2.rectangle(temp, ((pin-1)*47+10,self.cam.yDSize-70) , (pin*47+10,self.cam.yDSize-25) , (0,0,255) , 2)		
		cv2.imshow('Error', temp)
		cv2.moveWindow('Error',550,50)
		cv2.waitKey(50)
		return
	def drawErrorRectangleOverROI(self,ROI,img):
		cv2.rectangle(img,(ROI[0],ROI[1]),(ROI[2],ROI[3]),(0,0,255),3)

if __name__ == "__main__":
	cam = ImageCapture()
	scanner = QA_control(cam)
	while True:
		currentSet = cam.getExtImageSet()
		
		#BotPinSet=scanner.currentSet['botPinRowBin']
		#TopPinSet=scanner.currentSet['topPinRowBin']
		#TopPinSet = np.uint8(TopPinSet)
		#BotPinSet = np.uint8(BotPinSet)
		#tbox=scanner.analyser.findContourBoxes(scanner.cam.binaryPin)
		#bbox=scanner.analyser.findContourBoxes(BotPinSet)
		#for box in tbox:
		#	cv2.drawContours(scanner.cam.raw,[box],0,(0,0,255),2)
		#for box in bbox:
		#	cv2.drawContours(scanner.cam.raw,[box],0,(0,128,255),2)
		#cv2.imshow('TPR',scanner.cam.raw)
		#cv2.waitKey(100)
		start_time = time.time()
		if scanner.fullScan() is True:
			print ("Pass")
		end_time = time.time()
		#print("time taken {0}".format(end_time-start_time))
		time.sleep(1)
	foo.cap.stream.release()
	cv2.destroyAllWindows()	


		
