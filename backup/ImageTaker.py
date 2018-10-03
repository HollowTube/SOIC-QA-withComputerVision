import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import time
import math
from scipy.spatial import distance as dist
from scipy.stats import linregress
import csv
from imutils.video import WebcamVideoStream
import imutils
from ImageExtract import Analyser

class ImageTaker(object):

	def __init__(self):
		# Define these parameters for different package type.
		self.pinNumber=20
		self.xSize=510
		self.xDSize=500
		self.ySize=440
		self.yDSize=390
		self.xOff=50
		self.yOff=20
		self.pinRange=110
		self.thresholdPin = 185
		self.thresholdLetter = 185
		self.xadj=15
		self.yadj=55
		self.centerLetteringZone = (110, 240, 250, 320)
		self.cap = WebcamVideoStream(src=0).start()

		#ROIs in the format of (x1,y1,x2,y2)
		self.mainZone = np.int0((0,0,self.xSize,self.ySize))
		self.topPinRowZone = (0, 0,self.xDSize,70)
		self.botPinRowZone = (0, self.yDSize-70, self.xDSize,self.yDSize)
		self.BLPinZone = (0, 0, self.xSize, self.pinRange)
		self.URPinZone = (0, 0, self.xSize, self.pinRange)		
		self.raw = np.float32()
		self.binaryPin = np.float32()
		self.binaryLettering= np.float32()

	#updates stored images within object
	#3 images stored, raw, binary for the pins, and binary for the lettering
	def captureBinarizePinsAndLettering(self):
		#colored image
		img_raw = self.cap.read()

		# crop image to proper size
		img=img_raw[self.yOff:self.yOff+self.ySize,self.xOff:self.xOff+self.xSize]

		# Flip the upsize down image (flip the camera ???)
		#img=cv2.flip(img1,-1)

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
		return img,binaryPin,binaryLettering

	# This function is used to capture primary image, the object may not be in the camera view 
	def capture_raw(self):
		#colored image
		img_raw = self.cap.read()

		# crop image to proper size
		img=img_raw[self.yOff:self.yOff+self.ySize,self.xOff:self.xOff+self.xSize]

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
		return img,binaryPin,binaryLettering


	def findOC(self,img):
		im2, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours = np.array(contours)
		boxes = []
		for cnt in contours:
			area = cv2.contourArea(cnt)
			perimeter =cv2.arcLength(cnt,True)
			if(area >320 and area <500 and perimeter <100):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				boxes.append(box)
		boxes = np.array(boxes)
		boxavr=[]
		# Merge four coordinate of the rectagle into 1
		for box in boxes:
			#cv2.drawContours(bw_image,[box],-1,(128,0,128),2)
			#print box
			packet=((box[0,0]+box[1,0]+box[2,0]+box[3,0])/4,(box[0,1]+box[1,1]+box[2,1]+box[3,1])/4)
			packet=np.array(packet)
			boxavr.append(packet)
		boxavr=np.array(boxavr)
		last =len(boxavr)
		xSorted=boxavr[np.argsort(boxavr[:, 0]), :]
		if( xSorted[0,1] <xSorted[1,1]):
			bl=xSorted[0]
			tl=xSorted[1]
		else:
			bl=xSorted[1]
			tl=xSorted[0]
		if( xSorted[last-1,1] >xSorted[last-2,1]):
			tr=xSorted[-1]
			br=xSorted[-2]
		else:
			tr=xSorted[-2]
			br=xSorted[-1]		
		newbox=(bl,br,tr,tl)
		newbox=np.array(newbox)		
		return newbox

	
	# This function will capture and then extract only the image of the device
	# Run this function when we are certain a device is present in the spocket.
	def captureExtract(self):
		
		#colored image
		img_raw = self.cap.read()
		# crop image to proper size
		img=img_raw[self.yOff:self.yOff+self.ySize,self.xOff:self.xOff+self.xSize]
		#conversion to greyscale
		gray_raw = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		
		#application of gaussian filter for otsu thresholding
		blur = cv2.GaussianBlur(gray_raw,(5,5),0)
		ret1,th1 =cv2.threshold(blur,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)

		# Find square that belong to upper level of the pin
		bw_image = np.uint8(binaryPin)
		(bl,br,tr,tl)=self.findOC(bw_image)
		#calculate rotation
		xdiff,ydiff=br-bl
		if ydiff==0:
			angle=0
		else:	
			angle=np.arctan2(ydiff,xdiff)*180/np.pi		
		# Now rotate image
		cols,rows = gray_raw.shape
		M= cv2.getRotationMatrix2D((rows,cols),angle,1)
		gray_rot=cv2.warpAffine(gray_raw,M,(rows,cols))
		# Find contour again 
		oldbox=(bl,br,tr,tl)
		oldbox=np.array(oldbox)
		blur = cv2.GaussianBlur(gray_rot,(7,7),0)
		ret1,th1 =cv2.threshold(blur,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)
		bw_image = np.uint8(binaryPin)
		(bl,br,tr,tl)=self.findOC(bw_image)
		# Now the new boundary is found crop the new image to proper size

		final_raw=gray_rot[bl[1]-self.yadj:tr[1]+self.yadj,bl[0]-self.xadj:tr[0]+self.xadj]
		(self.yDSize,self.xDSize)=final_raw.shape
		# Redefine the new zone for top and bot pin row
		self.topPinRowZone = (0, 0,self.xDSize,70)
		self.botPinRowZone = (0, self.yDSize-70, self.xDSize,self.yDSize)
		print self.xDSize,self.yDSize
		cv2.drawContours(gray_raw,[oldbox],-1,(128,0,128),2)
		cv2.imshow('capture',gray_raw)
		newbox=(bl,br,tr,tl)
		newbox=np.array(newbox)
		cv2.drawContours(final_raw,[newbox],-1,(128,0,128),2)
		temp=self.cropROI(self.botPinRowZone ,final_raw)
		print self.botPinRowZone 
		print self.topPinRowZone 
		cv2.imshow('top pin',temp)
		cv2.imshow('rot',final_raw)

		cv2.waitKey(1)
		return newbox

		self.raw = img
		self.binaryPin = binaryPin
		self.binaryLettering  = binaryLettering
		return img,binaryPin,binaryLettering

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
		mainBin = self.cropROI(self.mainZone,self.binaryPin.copy())
		topPinRowBin = self.cropROI(self.topPinRowZone,mainBin) 
		botPinRowBin = self.cropROI(self.botPinRowZone,mainBin)
		BLPinBin = self.cropROI(self.BLPinZone,mainBin)
		URPinBin = self.cropROI(self.URPinZone,mainBin)
		return topPinRowBin,botPinRowBin,BLPinBin,URPinBin 

	def cropOutLetteringinBlackandWhite(self):
		main = self.cropROI(self.mainZone,self.binaryLettering.copy())
		centerLetteringBin = self.cropROI(self.centerLetteringZone,main)
		return centerLetteringBin

	def getNewImageSet(self):
		self.captureBinarizePinsAndLettering()
		self.currentImageSet = self.makeImageSet()
		return self.currentImageSet

	def makeImageSet(self):
		topPinRowBin,botPinRowBin,BLPinBin,URPinBin  = self.cropOutPinZonesinBlackandWhite()
		centerLetteringBin = self.cropOutLetteringinBlackandWhite()
		imageSet = {}
		imageSet['topPinRowBin'] = 	topPinRowBin
		imageSet['botPinRowBin'] = 	botPinRowBin
		imageSet['BLPinBin'] = 	BLPinBin
		imageSet['URPinBin'] = 	URPinBin
		imageSet['centerLetteringBin'] = centerLetteringBin
		return imageSet

	def getCopyOfImageSet(self):
		imageSet = self.makeImageSet()
		return imageSet
	def getRawImg(self):
		return self.raw.copy()
	def getPinBin(self):
		return self.binaryPin.copy()
	def getLetteringBin(self):
		return self.binaryLettering.copy()
		
if __name__ == "__main__":
	print("starting camera")
	cam = ImageTaker()
	print("starting Display")
	#display = DisplayManager(cam)
	while True:
		cam.captureExtract()
		
		pass
	foo.cap.stream.release()
	cv2.destroyAllWindows()
