import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import time
import math
from scipy.stats import linregress
import csv
from imutils.video import WebcamVideoStream
import imutils


class ImageTaker(object):

	def __init__(self):
		self.cap = WebcamVideoStream(src=0).start()

		self.thresholdPin = 198
		self.thresholdLetter = 180
	
		#ROIs in the format of (x1,y1,x2,y2)
		self.mainZone = np.int0((45, 10, 600, 450))
		self.topPinRowZone = (30, 10, 540, 150)
		self.botPinRowZone = (30, 350, 540, 430)
		self.centerLetteringZone = (297, 259, 459, 323)
		self.BLPinZone = (60, 350, 100, 419)
		self.URPinZone =(470, 10, 520, 80)

		self.raw = np.float32()
		self.binaryPin = np.float32()
		self.binaryLettering= np.float32()

	#updates stored images within object
	#3 images stored, raw, binary for the pins, and binary for the lettering
	def captureBinarizePinsAndLettering(self):
		#colored image
		img = self.cap.read()
		
		#conversion to greyscale
		gray_raw = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		
		#application of gaussian filter for otsu thresholding
		blur = cv2.GaussianBlur(gray_raw,(5,5),0)

		ret1,th1 =cv2.threshold(blur,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)

		ret2,th2 = cv2.threshold(blur,self.thresholdLetter,255,cv2.THRESH_BINARY)
		binaryLettering = np.float32(th2)

		self.raw = img
		self.binaryPin = binaryPin
		self.binaryLettering  = binaryLettering

	def cropROI(self, ROI,img):
		return img[ROI[1]:ROI[3],ROI[0]:ROI[2]]	
	
	def cropOutAllZonesinColor(self):
		self.main = self.cropROI(self.mainZone,self.raw)

		self.topPinRow = self.cropROI(self.topPinRowZone,self.main) 
		self.botPinRow = self.cropROI(self.botPinRowZone,self.main)

		self.centerLettering = self.cropROI(self.centerLetteringZone,self.main)
		self.BLPin = self.cropROI(self.BLPinZone,self.main)
		self.URPin = self.cropROI(self.URPinZone,self.main) 

	def cropOutPinZonesinBlackandWhite(self):
		mainBin = self.cropROI(self.mainZone,self.binaryPin)

		topPinRowBin = self.cropROI(self.topPinRowZone,self.main) 
		botPinRowBin = self.cropROI(self.botPinRowZone,self.main)
		BLPinBin = self.cropROI(self.BLPinZone,self.main)
		URPinBin = self.cropROI(self.URPinZone,self.main)
		return topPinRowBin,botPinRowBin,BLPinBIn,URPinBin 

	def cropOutLetteringinBlackandWhite(self):
		main = self.cropROI(self.mainZone,self.binaryPin)
		centerLetteringBin = self.cropROI(self.centerLetteringZone,self.main)
		return centerLetterBin

	def addROIRectangles(self):
		img = self.main
		cv2.rectangle(self.raw,(self.mainZone[0],self.mainZone[1]),(self.mainZone[2],self.mainZone[3]),(255,255,0),3)
		cv2.rectangle(img,(self.topPinRowZone[0],self.topPinRowZone[1]),(self.topPinRowZone[2],self.topPinRowZone[3]),(0,255,0),3)
		cv2.rectangle(img,(self.botPinRowZone[0],self.botPinRowZone[1]),(self.botPinRowZone[2],self.botPinRowZone[3]),(0,255,0),3)
		cv2.rectangle(img,(self.centerLetteringZone[0],self.centerLetteringZone[1]),(self.centerLetteringZone[2],self.centerLetteringZone[3]),(0,255,0),3)
		cv2.rectangle(img,(self.BLPinZone[0],self.BLPinZone[1]),(self.BLPinZone[2],self.BLPinZone[3]),(0,255,0),3)
		cv2.rectangle(img,(self.URPinZone[0],self.URPinZone[1]),(self.URPinZone[2],self.URPinZone[3]),(0,255,0),3)
		return img

if __name__ == "__main__":
	print("starting camera")
	foo = ImageTaker()
	print("starting Display")
	while True:
		foo.captureBinarizePinsAndLettering()
		foo.cropOutAllZonesinColor()
		foo.addROIRectangles()
		raw = foo.raw
		cropped = foo.main
		cropcrop = foo.topPinRow
		cv2.imshow('raw',raw)
		cv2.imshow('crop',cropped)
		cv2.imshow('crop of crop', cropcrop)
		cv2.waitKey(1)
	
	foo.cap.stream.release()
	cv2.destroyAllWindows()
