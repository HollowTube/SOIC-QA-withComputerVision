import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
from ImageTaker import ImageTaker
from Analyser import Analyser
import numpy as np

	
class DisplayManager(object):
	def __init__(self,cam):
		self.cam = cam
		self.Analyser = Analyser(cam)

	def printROI(self):
		r = cv2.selectROI(self.cam.raw)
		x1 = r[0]
		y1 = r[1]
		x2 = r[0]+r[2]
		y2 = r[1] +r[3]
		print(x1,y1,x2,y2)
		print(y1,y2, x1,x2)

	def addROIRectangles(self,img):
		main = self.cam.cropROI(self.cam.mainZone,img)
		self.drawRectangleOverROI(self.cam.mainZone,img)
		self.drawRectangleOverROI(self.cam.topPinRowZone,main)
		self.drawRectangleOverROI(self.cam.botPinRowZone,main)
		self.drawRectangleOverROI(self.cam.centerLetteringZone,main)
		self.drawRectangleOverROI(self.cam.BLPinZone,main)
		self.drawRectangleOverROI(self.cam.URPinZone,main)
		return img

	def displayError(self, zone = None):
		img = self.cam.raw.copy()
		mainCopy = self.cam.cropROI(self.cam.mainZone,img)
		if zone == "Missing":
			self.drawErrorRectangleOverROI(self.cam.centerLetteringZone,mainCopy)
		elif zone == "Out of Tray":
			self.drawErrorRectangleOverROI(self.cam.centerLetteringZone,mainCopy)
			self.drawErrorRectangleOverROI(self.cam.centerLetteringZone,mainCopy)
		elif zone == "Top Pins":
			self.drawErrorRectangleOverROI(self.cam.topPinRowZone,mainCopy)	
		elif zone == "Bot Pins":
			self.drawErrorRectangleOverROI(self.cam.botPinRowZone,mainCopy)

		if zone is None:
			cv2.imshow('Viewer',self.cam.raw)
		else:
			cv2.imshow('Error',Copy)
		cv2.waitKey(1)

	def displayDebugInformation(self):
		img = self.cam.raw.copy()
		main = self.cam.cropROI(self.cam.mainZone,img)
		self.addROIRectangles(img)
		self.drawContourBoxes(main)
		cv2.imshow('Debug',img)		

	def drawRectangleOverROI(self,ROI,img):
		cv2.rectangle(img,(ROI[0],ROI[1]),(ROI[2],ROI[3]),(0,255,0),3)

	def drawErrorRectangleOverROI(self,ROI,img):
		cv2.rectangle(img,(ROI[0],ROI[1]),(ROI[2],ROI[3]),(0,0,255),3)

	def displayBinary(self):
		bw_img = self.cam.binaryPin.copy()
		cv2.imshow('Binary', bw_img)

	def drawContourBoxes(self,img):

		topBoxes = self.Analyser.findContourBoxes(self.cam.topPinRowBin)
		botBoxes = self.Analyser.findContourBoxes(self.cam.botPinRowBin)

		topCropped = cam.cropROI(self.cam.topPinRowZone,img)
		botCropped = cam.cropROI(self.cam.botPinRowZone,img)

		for box in topBoxes:
			cv2.drawContours(topCropped,[box],0,(0,0,255),2)
		for box in botBoxes:
			cv2.drawContours(botCropped,[box],0,(0,0,255),2)
		
	def showDebugWindows(self):
			cv2.imshow('Pin',self.cam.binaryPin)
			cv2.moveWindow('Pin',0,512)
			cv2.imshow('Marking',self.cam.binaryLettering)
			cv2.moveWindow('Marking',640,512)
			self.displayDebugInformation()

if __name__ == "__main__":
	print("starting camera")
	cam = ImageTaker()
	display = DisplayManager(cam)
	print("starting Display")
	while True:
		cam.captureBinarizePinsAndLettering()
		cam.cropOutAllZonesinColor()
		cam.cropOutPinZonesinBlackandWhite()
		cam.cropOutLetteringinBlackandWhite()
		#display.drawTopContours(cam.topPinRowBin,cam.topPinRow)
		#cv2.imshow("raw", cam.raw)
		cv2.imshow('raw', cam.raw)
		display.showDebugWindows()
		display.displayBinary()
		cv2.waitKey(1)

	cam.cap.stream.release()
	cv2.destroyAllWindows()
