import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import time
import math
from scipy.stats import linregress


class Analyser(object):
	#Pin spacing parameters
	def __init__(self,cam):
		self.maxPinDist = 50
		self.minPinDist = 43
		
		#ROIs in the format of (x1,y1,x2,y2)
		self.topPinRow = (30, 10, 540, 150)
		self.botPinRow = (30, 350, 540, 440)
		self.centerLettering = (297, 259, 459, 323)
		self.BLPin = (60, 350, 100, 419)
		self.URPin =(470, 10, 520, 80)

		self.cam = cam

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
		#self.displayDebug()
		return True

	def checkPin(self,topPins,botPins):

		cornersTop = self.topCornersUsingContour(topPins)
		cornersTop = self.getTop20(cornersTop)
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

		if self.checkLinearity(cornersTop) is False:
			print("Top pins not aligned")
			#self.displayDebug(zone = "Top Pins")
			return False

		if self.checkLinearity(cornersBot) is False:
			print("Bot pins not aligned")
			#self.displayDebug(zone = "Bot Pins")
			return False

		if self.checkSpacing(cornersTop) is False:
			print("Top spacing off")
			#self.displayDebug(zone = "Top Pins")
			return False
		if self.checkSpacing(cornersBot) is False:
			print("Bot spacing off")
			#self.displayDebug(zone = "Bot Pins")
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
		m,c = linregress(x,y)[:2]
		error = np.absolute(y-(m*x + c))
		for iterator in range (0,len(error)):
			if error[iterator] > 3:
				#print ("Absolute error array", error)
				print("error", error[iterator])
				print("Error CHECK PIN {0}".format(iterator//2))
		if max(error) >  3:
			return False

	def checkSpacing(self,corners):
		error = []
		for x in range(0,len(corners) - 2):
			dist = np.linalg.norm(corners[x]-corners[x+2])
			error.append(dist)
		for dist in error:
			if(dist > self.maxPinDist or dist < self.minPinDist):
				return False
		return True

	def topCornersUsingContour(self,bw_img):
		contourBoxes = self.findContourBoxes(bw_img)
		topCorners = []
		for box in contourBoxes:
			top2Indexes = np.argpartition(box[:, 1], 2)[:2]
			for corner in top2Indexes:
				topCorners.append(box[corner])
		return topCorners


	def botCornersUsingContour(self,bw_img):
		contourBoxes = self.findContourBoxes(bw_img)
		botCorners = []
		for box in contourBoxes:
			bot2Indexes = np.argpartition(box[:, 1], 2)[-2:]
			for corner in bot2Indexes:
				botCorners.append(box[corner])
		return botCorners


	def findContourBoxes(self,bw_img):
		bw_img = np.uint8(bw_img)
		im2, contours, hierarchy = cv2.findContours(bw_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours = np.array(contours)
		boxes = []
		for cnt in contours:
			if(cv2.contourArea(cnt) > 140):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				boxes.append(box)
		return boxes

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
if __name__ == "__main__":
	print("starting camera")
	foo = WebcamVideoStream(src = 0).start()
	print("starting Display")

	while True:
		if display.showimage:
			img = foo.read()
			cv2.imshow('raw', img)
			cv2.waitKey(1)
			display.reset()
	
	foo.stop()
	foo.stream.release()
	cv2.destroyAllWindows()
