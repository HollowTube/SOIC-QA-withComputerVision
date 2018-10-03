import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import time
import math
from scipy.stats import linregress
import csv

from imutils.video import WebcamVideoStream
import imutils
from threading import Thread

class camera(object):

	def __init__(self):
		self.cap = WebcamVideoStream(src=0).start()
		#Binary threshold for image binarization
		self.thresholdPin = 180
		self.thresholdLetter = 170

		#ROIs in the format of (x1,y1,x2,y2)
		self.topPinRow = (50, 20, 570, 120)
		self.botPinRow = (50, 350, 570, 450)
		self.centerLettering = (160, 250, 320, 320)
		self.BLPin = (80, 350, 150, 435)
		self.URPin =(470, 30, 540, 100)

		#Pin spacing parameters
		self.maxPinDist = 52
		self.minPinDist = 42
		self.debugon=1
		raw,binaryPin, binaryLetters = self.captureBinarizePinsAndLettering()
		self.addROIRectangles(raw)
		cv2.imshow('Main',raw)
		cv2.moveWindow('Main',0,0)
		if self.debugon > 0:
			cv2.imshow('Pin',binaryPin)
			cv2.moveWindow('Pin',0,512)
			cv2.imshow('Marking',binaryLetters)
			cv2.moveWindow('Marking',640,512)
		cv2.waitKey(1)
	"""def importParameters(self, filename):
		parameterFile = open(filename,"r")
		paramList = []
		for line in parameterFile:
			if line[0] is not '#' and line is not '\n':
				paramList.append(line[:-1])
		print(list)
		self.binThresholdPin = int(paramList[0])
		self.binThresholdLetter = int(paramList[1])
	
		#ROIs in the format of (x1,y1,x2,y2)
		self.topPinRow = self.convertToArray(paramList[2])
		self.botPinRow = self.convertToArray(paramList[3])
		self.centerLettering = self.convertToArray(paramList[4])
		self.BLPin = self.convertToArray(paramList[5])
		self.URPin =self.convertToArray(paramList[6])
		#Pin spacing parameters
		self.maxPinDist = int(paramList[7])
		self.minPinDist = int(paramList[8])
	def convertToArray(self,foo):
		return [int(x) for x in foo.split(",")]"""
	
	def fullScan(self):
		for x in range (0,3):
			raw,binaryPin, binaryLetters = self.captureBinarizePinsAndLettering()
			cv2.imshow('Main',raw)
			if self.debugon > 0:
				cv2.imshow('Pin',binaryPin)
				cv2.imshow('Marking',binaryLetters)
			cv2.waitKey(1)
		# Crop for top and bottom pin check	
		topBin = self.cropROI(self.topPinRow,binaryPin)
		botBin = self.cropROI(self.botPinRow,binaryPin)
		fail_type=0
		if  self.checkFlip(binaryLetters) is False:
			print("Marking not found")
			fail_type=1
			raw= cv2.rectangle(raw,(self.centerLettering[0],self.centerLettering[1]),(self.centerLettering[2],self.centerLettering[3]),(0,255,0),3)
		elif self.checkOutOfTray(binaryLetters) is False:
			print("Pin not found")
			fail_type=2
			raw= cv2.rectangle(raw,(self.topPinRow[0],self.topPinRow[1]),(self.topPinRow[2],self.topPinRow[3]),(0,255,0),3)
			raw= cv2.rectangle(raw,(self.botPinRow[0],self.botPinRow[1]),(self.botPinRow[2],self.botPinRow[3]),(0,255,0),3)
		elif self.checkPin(topBin,botBin) is False:
			fail_type=3
		
		cv2.imshow('Main',raw)
		cv2.waitKey(10)

		return fail_type

	def checkPin(self,topPins,botPins):
		cornersTop = self.topCornersUsingContour(topPins)
		cornersTop = self.getTop20(cornersTop)
		if cornersTop is False:
			print("Top pins missing")
			self.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.botCornersUsingContour(botPins)
		cornersBot = self.getBot20(cornersBot)
		if cornersBot is False:
			print("Bottom pins missing")
			#self.displayDebug(zone = "Bot Pins")
			return False
		if self.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			#self.displayDebug(zone = "Top Pins")
			return False
		if self.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			#self.displayDebug(zone = "Bot Pins")
			return False
		if self.checkSpacing(cornersTop) is False:
			print("Top row pin spacing off")
			#self.displayDebug(zone = "Top Pins")
			return False
		if self.checkSpacing(cornersBot) is False:
			print("Bottom row spacing off")
			#self.displayDebug(zone = "Bot Pins")
			return False
		return True

	def checkFlip(self,img):
		roi =  img[self.centerLettering[1]:self.centerLettering[3],self.centerLettering[0]:self.centerLettering[2]]
		if self.debugon >0:
			print roi.mean()
		if (roi.mean()>10):
			return True
		else:
			return False

	def checkOutOfTray(self,img):
		BL = img[self.topPinRow[1]:self.topPinRow[3],self.topPinRow[0]:self.topPinRow[2]]
		UR =  img[self.botPinRow[1]:self.botPinRow[3],self.botPinRow[0]:self.botPinRow[2]]
		if self.debugon >0:		
			print BL.mean() , UR.mean()
		if BL.mean()>20 and UR.mean()>20:
			return  True
		else:
			return False

	def checkLinearity(self,arr):
		arr = np.array(arr)
		if len(arr) < 10:
			print("small")
			return False
		x,y  = np.hsplit(arr,2)
		x = np.ravel(x)
		y = np.ravel(y)
		m,c,rValue,pValue = linregress(x,y)[:4]
		error = np.absolute(y-(m*x + c))
		for iterator in range (0,len(error)):
			if error[iterator] > 3:
				#print ("Absolute error array", error)
				#print("error", error[iterator])
				#print(pValue)
				print("Error CHECK PIN {0}".format(iterator//2))
		if max(error) >  3:
			return False
		return True

	def checkSpacing(self,corners):
		error = []
		for x in range(0,len(corners) - 2):
			dist = np.linalg.norm(corners[x]-corners[x+2])
			error.append(dist)
		x=0
		for dist in error:
			x=x+1
			if(dist > self.maxPinDist or dist < self.minPinDist):
				print("pin %d Space=%3.0f" % (x/2+1,dist))
				return False
		return True

	#returns raw and 2 binary imgs
	def captureBinarizePinsAndLettering(self):
		#colored image read 4 frame
		for x in range(0,3):		
			img_in = self.cap.read()
		#	cv2.imshow('Main',img)
		#	cv2.waitKey(1)
		#conversion to greyscale
		img=cv2.flip(img_in,-1)
		gray_raw = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		#application of gaussian filter for otsu thresholding
		blur = cv2.GaussianBlur(gray_raw,(5,5),0)
		ret1,th1 =cv2.threshold(blur,self.thresholdPin,255,cv2.THRESH_BINARY)
		binaryPin = np.float32(th1)
		ret2,th2 = cv2.threshold(blur,self.thresholdLetter,255,cv2.THRESH_BINARY)
		binaryLettering = np.float32(th2)
		return img, binaryPin,binaryLettering

	def printROI(self):
		r = cv2.selectROI(raw_img)
		#print(r)
		x1 = r[0]
		y1 = r[1]
		x2 = r[0]+r[2]
		y2 = r[1] +r[3]
		print(x1,y1,x2,y2)
		print(y1,y2, x1,x2)
		#imCrop = binary[int(y1):int(y2), int(x1):int(x2)]
		#print(imCrop.mean())

	def addROIRectangles(self,img):
		
		img= cv2.rectangle(img,(self.topPinRow[0],self.topPinRow[1]),(self.topPinRow[2],self.topPinRow[3]),(0,255,0),3)
		img= cv2.rectangle(img,(self.botPinRow[0],self.botPinRow[1]),(self.botPinRow[2],self.botPinRow[3]),(0,255,0),3)
		img= cv2.rectangle(img,(self.centerLettering[0],self.centerLettering[1]),(self.centerLettering[2],self.centerLettering[3]),(0,255,0),3)
		img= cv2.rectangle(img,(self.BLPin[0],self.BLPin[1]),(self.BLPin[2],self.BLPin[3]),(0,255,0),3)
		img= cv2.rectangle(img,(self.URPin[0],self.URPin[1]),(self.URPin[2],self.URPin[3]),(0,255,0),3)
		return img

	def getBot20(self,corners):

		"""preprocessing array"""
		arr= np.array(corners)
		# Check the number of shape
		if arr.shape[0] < 40:
			return []
		arr = arr.reshape(arr.shape[0],2)

		sortIndByX = np.lexsort((arr[:,1],arr[:,0]))
		sortedByX = arr[sortIndByX]
		bot20 = []

		#collecting corners into packets of 4 and taking the bottom 2
		for foo in range(0,10):
			#grouping into 4
			packet = [sortedByX[foo*4],sortedByX[foo*4+1],sortedByX[foo*4+2],sortedByX[foo*4+3]]
			packet = np.array(packet)	
			
			#getting the bottom indices
			bot2Ind = np.lexsort((packet[:,0],packet[:,1]))[2:]

			#appending to array
			bot20.append(packet[bot2Ind[0]])
			bot20.append(packet[bot2Ind[1]])

		bot20 = np.array(bot20)
		finalSortIndbyX = np.lexsort((bot20[:,1],bot20[:,0]))

		finalBot = bot20[finalSortIndbyX]
		
		return finalBot

	def getTop20(self,corners):
		arr= np.array(corners)
		#print(arr.shape)
		if arr.shape[0] < 40:
			return []
		arr = arr.reshape(arr.shape[0],2)

		"""
		top20Indices = np.argpartition(arr[:, 1], 20)[:20]
		top20 = arr[top20Indices[0]]
		for foo in top20Indices[1:]:
			top20 = np.vstack((top20,arr[foo]))
		"""
		sortInd = np.lexsort((arr[:,1],arr[:,0]))
		top20 = arr[sortInd]

		finalTop = []
		for foo in range(0,10):
			packet = [top20[foo*4],top20[foo*4+1],top20[foo*4+2],top20[foo*4+3]]
			packet = np.array(packet)
			#print(packet)	
			top2Ind = np.lexsort((packet[:,0],packet[:,1]))[:-2]
			#print(packet[top2Ind])
			finalTop.append(packet[top2Ind[0]])
			finalTop.append(packet[top2Ind[1]])
		#print("top")
		finalTop = np.array(finalTop)
		sortInd = np.lexsort((finalTop[:,1],finalTop[:,0]))
		finalTop = finalTop[sortInd]
		#print(finalTop)
		#print(finalTop.shape)
		
		return finalTop

	def displayBasicView(self):
		raw_img,binaryPin, binaryLetter = self.captureBinarizePinsAndLettering()
		
		topRaw = self.cropROI(self.topPinRow,raw_img)
		topBin = self.cropROI(self.topPinRow,binaryPin)

		botRaw = self.cropROI(self.botPinRow,raw_img)
		botBin = self.cropROI(self.botPinRow,binaryPin)
		
		"""overlay for ROI and Contours"""
		self.addROIRectangles(raw_img)
		#self.drawBotContours(botBin,botRaw)
		#self.drawTopContours(topBin,topRaw)

		"""Final image display"""
		cv2.imshow('Raw', raw_img)
		cv2.waitKey(1)
	
	def topCornersUsingContour(self,bw_img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		topCorners = []
		for cnt in contours:
			#print(cv2.contourArea(cnt))
			if(cv2.contourArea(cnt) > 140):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				top2Indexes = np.argpartition(box[:, 1], 2)[:2]
				for corner in top2Indexes:
					topCorners.append(box[corner])
		return topCorners

	def botCornersUsingContour(self,bw_img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		botCorners = []
		for cnt in contours:
			#print(cv2.contourArea(cnt))
			if(cv2.contourArea(cnt) > 140):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				bot2Indexes = np.argpartition(box[:, 1], 2)[-2:]
				for corner in bot2Indexes:
					botCorners.append(box[corner])
		return botCorners
		
	def drawTopContours(self,bw_img,img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		for cnt in contours:
			if(cv2.contourArea(cnt) > 150):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				cv2.drawContours(img,[box],0,(0,0,255),2)




	def drawBotContours(self,bw_img,img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		for cnt in contours:
			if(cv2.contourArea(cnt) > 150):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				cv2.drawContours(img,[box],0,(0,0,255),2)

	def cropROI(self, ROI,img):
		return img[ROI[1]:ROI[3],ROI[0]:ROI[2]]

	def displayRaw(self):
		img  = self.captureBinarizePinsAndLettering()[0]
		cv2.imshow('name', img)
		cv2.waitKey(500)
	def startDisplayThread(self):
		try:
			_thread.start_new_thread(displayRaw,("foo",))
		except:
			print("Failed to start Thread")

if __name__ == "__main__":
	cam = camera()
	print("Initializing...")
	#cam.importParameters("20Pins.txt")
	print("Complete")
	


	
	while True:
		cam.displayRaw()

		if cv2.waitKey(1) & 0xFF == ord('q'):
			start = time.time()
			cam.fullScan()
			end = time.time()
			seconds = end - start
			print ("Time taken : {0} seconds".format(seconds))
		elif cv2.waitKey(1) & 0xFF == ord('c'):
			break
	thread1.join()
	cam.cap.stop()
	cv2.destroyAllWindows()
