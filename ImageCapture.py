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
from ImageAnalyse import Analyser

class ImageCapture(object):

	def __init__(self):
		# Define these parameters for different package type.
		self.pinNumber=20
		self.xSize=510
		self.xDSize=470
		self.ySize=440
		self.yDSize=340
		self.xOff=50
		self.yOff=35
		self.pinRange=110
		self.thresholdPin = 185
		self.thresholdLetter = 175
		self.xadj=30
		self.yadj=50
		self.centerLetteringZone = (250, 130, 390, 210)
		self.cap = WebcamVideoStream(src=0).start()

		#ROIs in the format of (x1,y1,x2,y2)
		self.mainZone = np.int0((0,0,self.xSize,self.ySize))
		self.topPinRowZone = (0, 0,self.xDSize,80)
		self.botPinRowZone = (0, self.yDSize-30, self.xDSize,self.yDSize+80)
		#self.topPinRowZone  = (0, 10, self.xSize, self.pinRange)
		#self.botPinRowZone  = (0, self.ySize-self.pinRange, self.xSize, self.ySize-25)
		self.BLPinZone = (0, 0, self.xSize, self.pinRange)
		self.URPinZone = (0, self.ySize-self.pinRange, self.xSize, self.ySize)		
		self.raw = np.float32()
		self.binaryPin = np.float32()
		self.binaryLettering = np.float32()

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
		#th1 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,2)	
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

		self.raw = gray_raw
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
			if(area >250 and area <550 and perimeter <100):
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
		#print bl
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
		if angle >10 or angle <10:
			angle=0
	
		# Now rotate image
		cols,rows = gray_raw.shape
		M= cv2.getRotationMatrix2D((rows,cols),angle,1)
		gray_rot=cv2.warpAffine(blur,M,(rows,cols))
		# Find contour again 
		oldbox=(bl,br,tr,tl)
		oldbox=np.array(oldbox)
		ret1,th1 =cv2.threshold(gray_rot,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)
		bw_image = np.uint8(binaryPin)
		
		(bl,br,tr,tl)=self.findOC(bw_image)
		# Now the new boundary is found crop the new image to proper size		
		#final_raw=gray_rot[bl[1]-self.yadj:tr[1]+self.yadj,bl[0]-self.xadj:tr[0]+self.xadj]
		
		final_raw=gray_rot[bl[1]-self.yadj:bl[1]+self.yDSize, bl[0]-self.xadj:bl[0]+self.xDSize]

		cv2.imshow('tt',final_raw)
		ret1,th1 =cv2.threshold(final_raw,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)
		ret1,th1 =cv2.threshold(final_raw,self.thresholdLetter,255,cv2.THRESH_BINARY)
		binaryLettering = np.float32(th1)
		# Redefine the new zone for top and bot pin row
		#(self.yDSize,self.xDSize)=final_raw.shape
		#self.topPinRowZone = (0, 0,self.xDSize,70)
		#self.botPinRowZone = (0, self.yDSize-70, self.xDSize,self.yDSize)
		self.raw = final_raw
		self.binaryPin = binaryPin
		self.binaryLettering  = binaryLettering
		return final_raw,binaryPin,binaryLettering

	def cropROI(self, ROI,img):
		return img[ROI[1]:ROI[3],ROI[0]:ROI[2]]	

	def cropOutPinZonesinBlackandWhite(self):
		mainBin = self.cropROI(self.mainZone,self.binaryPin)
		topPinRowBin = self.cropROI(self.topPinRowZone,mainBin) 
		botPinRowBin = self.cropROI(self.botPinRowZone,mainBin)
		BLPinBin = self.cropROI(self.BLPinZone,mainBin)
		URPinBin = self.cropROI(self.URPinZone,mainBin)
		return topPinRowBin,botPinRowBin,BLPinBin,URPinBin 

	def cropOutLetteringinBlackandWhite(self):
		main = self.cropROI(self.mainZone,self.binaryLettering)
		centerLetteringBin = self.cropROI(self.centerLetteringZone,main)
		return centerLetteringBin

	def getNewImageSet(self):
		self.captureBinarizePinsAndLettering()
		self.currentImageSet = self.makeImageSet()
		return self.currentImageSet

	def getExtImageSet(self):
		self.captureExtract()
		#self.currentImageSet = self.makeImageSet()
		topPinRowBin = self.cropROI(self.topPinRowZone,self.binaryPin) 
		botPinRowBin = self.cropROI(self.botPinRowZone,self.binaryPin)
		cv2.imshow('ttt',self.binaryPin)
		self.currentImageSet = {}
		self.currentImageSet['topPinRowBin'] = 	topPinRowBin
		self.currentImageSet['botPinRowBin'] = 	botPinRowBin
		self.currentImageSet['BLPinBin'] = 	self.binaryPin
		self.currentImageSet['URPinBin'] = 	self.binaryPin
		self.currentImageSet['centerLetteringBin'] = self.binaryPin
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
	cam = ImageCapture()
	print("starting Display")
	#display = DisplayManager(cam)
	while True:
		start_time = time.time()
		#(main,binary,letter)=cam.captureBinarizePinsAndLettering()		
		(main,binary,letter)=cam.captureExtract()
		end_time = time.time()
		print("time taken {0}".format(end_time-start_time))
		
		cv2.imshow('capture',main)

		temp=cam.cropROI(cam.botPinRowZone ,binary)
		#print cam.botPinRowZone 
		#print cam.topPinRowZone 
		cv2.imshow('top pin',temp)
		cv2.imshow('rot',binary)

		cv2.waitKey(1)
		pass
	foo.cap.stream.release()
	cv2.destroyAllWindows()
