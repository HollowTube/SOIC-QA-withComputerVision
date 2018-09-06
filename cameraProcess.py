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
class camera(object):

	def __init__(self):

		self.cap = WebcamVideoStream(src=0).start()
		#Binary threshold for image binarization
		self.thresholdPin = 198
		self.thresholdLetter = 180

		#ROIs in the format of (x1,y1,x2,y2)
		self.topPinRow = (50, 10, 540, 150)
		self.botPinRow = (50, 350, 540, 440)
		self.centerLettering = (297, 259, 459, 323)
		self.BLPin = (60, 350, 100, 419)
		self.URPin =(470, 10, 520, 80)

		#Pin spacing parameters
		self.maxPinDist = 50
		self.minPinDist = 43

	def importParameters(self, filename):
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
		return [int(x) for x in foo.split(",")]
	def fullScan(self):

		raw,binaryPin, binaryLetters = self.captureBinarizePinsAndLettering()
		topBin = self.cropROI(self.topPinRow,binaryPin)
		botBin = self.cropROI(self.botPinRow,binaryPin)
		if  self.checkFlip(binaryLetters) is False:
			print("No chip detected or flipped chip")
		
			print("Test result: FAILED")
			self.displayDebug(zone = "Missing")
			return False
	

		if self.checkOutOfTray(binaryLetters) is False:
			print("Chip out of Tray")
			print("Test result: FAILED")
			self.displayDebug(zone = "Out of Tray")
			return False
		
		if self.checkPin(topBin,botBin) is False:


			print("Test result: FAILED")
			
			return False
		
		print("Test result: PASSED")
		print("----------------")
		print
		self.displayDebug()
		return True

	def checkPin(self,topPins,botPins):


		cornersTop = self.topCornersUsingContour(topPins)
		cornersTop = self.getTop20(cornersTop)
		if cornersTop is []:
			print("Top pins missing")
			self.displayDebug(zone = "Top Pins")
			return False

		cornersBot = self.botCornersUsingContour(botPins)
		cornersBot = self.getBot20(cornersBot)
		if cornersBot is []:
			print("Bot pins missing")
			self.displayDebug(zone = "Bot Pins")
			return False

		if self.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			self.displayDebug(zone = "Top Pins")
			return False

		if self.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			self.displayDebug(zone = "Bot Pins")
			return False

		if self.checkSpacing(cornersTop) is False:
			print("Top spacing off")
			self.displayDebug(zone = "Top Pins")
			return False
		if self.checkSpacing(cornersBot) is False:
			print("Bot spacing off")
			self.displayDebug(zone = "Bot Pins")
			return False
		return True

	def checkFlip(self,img):
		roi =  img[self.centerLettering[1]:self.centerLettering[3],self.centerLettering[0]:self.centerLettering[2]]
		if (roi.mean()>30):
			return True
		else:
			return False

	def checkOutOfTray(self,img):
		BL = img[self.BLPin[1]:self.BLPin[3],self.BLPin[0]:self.BLPin[2]]
		UR =  img[self.URPin[1]:self.URPin[3],self.URPin[0]:self.URPin[2]]
		return BL.mean()>10 and UR.mean()>10



	def checkLinearity(self,arr):	
		x,y  = np.hsplit(arr,2)
		x = np.ravel(x)
		y = np.ravel(y)
		m,c,rValue,pValue = linregress(x,y)[:4]
		error = np.absolute(y-(m*x + c))
		for iterator in range (0,len(error)):
			if error[iterator] > 3:
				#print ("Absolute error array", error)
				print("error", error[iterator])
				print("Error CHECK PIN {0}".format(iterator//2))
		if max(error) >  3:
			return False
		
		#print("Pvalue: ",pValue)
		#print("R-Value: ", rValue)

	def checkSpacing(self,corners):
		error = []
		for x in range(0,len(corners) - 2):
			dist = np.linalg.norm(corners[x]-corners[x+2])
			error.append(dist)
		for dist in error:
			if(dist > self.maxPinDist or dist < self.minPinDist):

				return False
		return True

	#returns raw and 2 binary imgs
	def captureBinarizePinsAndLettering(self):

		#colored image
		#print("capturing")
		img = self.cap.read()
		#print("captured")
		#conversion to greyscale
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
		if arr.shape[0] < 20:
			return []
		arr = arr.reshape(arr.shape[0],2)

		"""getting to the twenty"""
		bot20Indices = np.argpartition(arr[:, 1], arr.shape[0]-20)[-20:]
		bot20 = arr[bot20Indices[0]]
		for foo in bot20Indices[1:]:
			bot20 = np.vstack((bot20,arr[foo]))
		sortInd = np.lexsort((bot20[:,1],bot20[:,0]))
		bot20 = bot20[sortInd]

		return bot20

	def getTop20(self,corners):
		arr= np.array(corners)
		if arr.shape[0] < 20:
			return []
		arr = arr.reshape(arr.shape[0],2)
		top20Indices = np.argpartition(arr[:, 1], 20)[:20]

		top20 = arr[top20Indices[0]]
		for foo in top20Indices[1:]:
			top20 = np.vstack((top20,arr[foo]))
		sortInd = np.lexsort((top20[:,1],top20[:,0]))
		top20 = top20[sortInd]

		return top20

	def displayDebug(self, zone = None):

		raw,binaryPin, binaryLetters = self.captureBinarizePinsAndLettering()
		rawCopy = raw.copy()
		if zone == "Missing":
			cv2.rectangle(rawCopy,(self.centerLettering[0],self.centerLettering[1]),(self.centerLettering[2],self.centerLettering[3]),(255,0,255),3)
		elif zone == "Out of Tray":
			cv2.rectangle(rawCopy,(self.BLPin[0],self.BLPin[1]),(self.BLPin[2],self.BLPin[3]),(255,0,255),3)
			cv2.rectangle(rawCopy,(self.URPin[0],self.URPin[1]),(self.URPin[2],self.URPin[3]),(255,0,255),3)
		elif zone == "Top Pins":
			cv2.rectangle(rawCopy,(self.topPinRow[0],self.topPinRow[1]),(self.topPinRow[2],self.topPinRow[3]),(255,0,255),3)
		elif zone == "Bot Pins":
			cv2.rectangle(rawCopy,(self.botPinRow[0],self.botPinRow[1]),(self.botPinRow[2],self.botPinRow[3]),(255,0,255),3)
		topBin = self.cropROI(self.topPinRow,binaryPin)
		botBin = self.cropROI(self.botPinRow,binaryPin)

		topRaw = self.cropROI(self.topPinRow,raw)
		botRaw = self.cropROI(self.botPinRow,raw)
		
		#self.drawTopContours(topBin,topRaw)
		#self.drawBotContours(botBin,botRaw)
		raw = self.addROIRectangles(raw)
		
		if zone is None:
			cv2.imshow('Viewer',raw)
		else:
			cv2.imshow('Error', rawCopy)
		cv2.waitKey(1)
	
	def topCornersUsingContour(self,bw_img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		topCorners = []
		for cnt in contours:
			if(cv2.contourArea(cnt) > 140):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				top2Indexes = np.argpartition(box[:, 1], 2)[:2]
				for corner in top2Indexes:
					topCorners.append(box[corner])
		#print(np.shape(topCorners))
		return topCorners

	def botCornersUsingContour(self,bw_img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		botCorners = []
		for cnt in contours:
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
			if(cv2.contourArea(cnt) > 135):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				cv2.drawContours(img,[box],0,(0,0,255),2)




	def drawBotContours(self,bw_img,img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		arr = np.array(contours)
		for cnt in contours:
			if(cv2.contourArea(cnt) > 100):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				cv2.drawContours(img,[box],0,(0,0,255),2)

	def cropROI(self, ROI,img):
		return img[ROI[1]:ROI[3],ROI[0]:ROI[2]]

if __name__ == "__main__":
	print("Initializing...")
	cam = camera()
	cam.importParameters("20Pins.txt")
	print("Complete")
	while True:
		"""capturing images"""
		raw_img,binaryPin, binaryLetter = cam.captureBinarizePinsAndLettering()
		#cam.drawContours(binaryPin,raw_img)
		

		topRaw = cam.cropROI(cam.topPinRow,raw_img)
		topBin = cam.cropROI(cam.topPinRow,binaryPin)
		cam.drawTopContours(topBin,topRaw)

		botRaw = cam.cropROI(cam.botPinRow,raw_img)
		botBin = cam.cropROI(cam.botPinRow,binaryPin)
		cam.drawBotContours(botBin,botRaw)
		#cv2.waitKey(0)
		
		"""overlay for ROI"""
		raw_img = cam.addROIRectangles(raw_img)

		"""ROI debuggin and printing"""
		#cam.printROI()

		"""Final image display"""
		cv2.imshow('Raw', raw_img)
		#cv2.imshow('Gray',binaryLetter)
		#cv2.imshow('Binary', binaryPin)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			start = time.time()
			if cam.fullScan() is False:
				pass
			end = time.time()
			seconds = end - start
			print ("Time taken : {0} seconds".format(seconds))
			time.sleep(2)
		elif cv2.waitKey(1) & 0xFF == ord('c'):
			break

	cam.cap.stop()
	cv2.destroyAllWindows()
"""
if __name__ == "__main__":
	on = OutputDevice(22)
	trigger = InputDevice(4)
	busy = OutputDevice(27)
	failFlag = OutputDevice(17)
	cam = camera()

	on.on()
	while True:
		print("Waiting for Trigger")
		
	    	while True:
			raw,binPin,binLetter = cam.captureBinarizePinsAndLettering()
			cv2.imshow('raw2',raw)

	    	busy.on()	
		failFlag.off()
		start_time = time.time()
	    	good = cam.fullScan()
	   	end_time = time.time()
		print("time taken {0}".format(end_time-start_time))
	    	if not good:
			failFlag.on()
			print("Fail")
	    	else:
			print("Pass")
		busy.off()
		time.sleep(1)
	    	while trigger.value is False:
			time.sleep(0.01)
"""
