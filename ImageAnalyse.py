import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import time
import math
from scipy.stats import linregress

class Analyser(object):
	#Pin spacing parameters
	def __init__(self,cam):
		self.maxPinDist = 52
		self.minPinDist = 42
		self.pinNumber = 10
		self.pinAlignTol = 1.9

		self.upperAreaThreshold = 450
		self.lowerAreaThreshold = 40
		self.upperPerimeterThreshold= 150
		self.lowerPerimeterThreshold = 30
		self.cam = cam
		self.debug = True

	def checkFlip(self,centerLettering):
		#print centerLettering.mean()
		if (centerLettering.mean()>30):
			return True
		else:
			return False

	def checkOutOfTray(self,BL,UR):
		#print BL.mean(),UR.mean()
		if BL.mean()>20 and UR.mean()>20:
			return  True
		else:
			return False

	def checkLinearity(self,arr):	
		# check if array has less than 10pin
		x,y  = np.hsplit(arr,2)
		x = np.ravel(x)
		y = np.ravel(y)
		m,c = linregress(x,y)[:2]
		error = np.absolute(y-(m*x + c))
		for pin in range (0,len(error)):
			if error[pin] > self.pinAlignTol:
				#print("error", error[pin])
				#print("Pin %d offset %5.2f" % (pin//2+1,error[pin]))
				return False,pin/2+1
#		if max(error) >  self.pinAlignTol:
#			return False
		return True,0

	def checkSpacing(self,corners):
		error = []
		for x in range(0,len(corners) - 2):
			dist = np.linalg.norm(corners[x]-corners[x+2])
			error.append(dist)
		x= 0
		for pin_dist in error:
			x=x+1
			if(pin_dist > self.maxPinDist or pin_dist < self.minPinDist):
				#print("Pin %d Space=%5.2f" % (x/2+1,pin_dist))
				return False,x/2+1
		return True,0
	
	def getLowestCorners(self,botPinsImg):
		bottomCorners = self.botCornersUsingContour(botPinsImg)
		lowestCorners = self.getLowerEdgePoints(bottomCorners)
		return lowestCorners
	
	def getHighestCorners(self,topPinsImg):
		topCorners = self.topCornersUsingContour(topPinsImg)
		highestCorners = self.getHigherEdgePoints(topCorners)
		return highestCorners

	def topCornersUsingContour(self,bw_img):
		contourBoxes = self.findContourBoxes(bw_img)
		topCorners = []
		for box in contourBoxes:
			top2Indexes = np.argpartition(box[:, 1], 2)[:2]
			for corner in top2Indexes:
				topCorners.append(box[corner])
		topCorners = np.array(topCorners)
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
		areaList = []
		perimeterList = []
		
		for cnt in contours:
			if(self.checkArea(cnt)  and self.checkPerimeter(cnt)):
				rect = cv2.minAreaRect(cnt)
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				boxes.append(box)
				areaList.append(cv2.contourArea(cnt))
				perimeterList.append(cv2.arcLength(cnt,True))
		boxes = np.array(boxes)
		#print (" Before A&P check) %d :%d",len(contours),len(boxes))
		return boxes

	def checkArea(self,cnt):
		area = cv2.contourArea(cnt)
		#print ("A: %d",area)
		if (area> self.lowerAreaThreshold and area < self.upperAreaThreshold):
			return True
		else:
			return False

	def checkPerimeter(self,cnt):
		perimeter = cv2.arcLength(cnt,True)
		#print ("P:%d",perimeter)
		if (perimeter > self.lowerPerimeterThreshold and perimeter < self.upperPerimeterThreshold):
			return True
		else:
			return False

	def getLowerEdgePoints(self,corners):

		"""preprocessing array"""
		arr = np.array(corners)
		# Check the number of shape
		if arr.shape[0] < 40:
			return []

		arr = arr.reshape(arr.shape[0],2)
		sortIndByX = np.lexsort((arr[:,1],arr[:,0]))
		sortedByX = arr[sortIndByX]

		lowerCorners = []

		#collecting corners into packets of 4 and taking the bottom 2
		for foo in range(0,10):
			#grouping into 4
			packet = [sortedByX[foo*4],sortedByX[foo*4+1],sortedByX[foo*4+2],sortedByX[foo*4+3]]
			packet = np.array(packet)	
			
			#getting the bottom indices
			bot2Ind = np.lexsort((packet[:,0],packet[:,1]))[2:]

			#appending to array
			lowerCorners.append(packet[bot2Ind[0]])
			lowerCorners.append(packet[bot2Ind[1]])

		lowerCorners = np.array(lowerCorners)
		finalSortIndbyX = np.lexsort((lowerCorners[:,1],lowerCorners[:,0]))

		finalBot = lowerCorners[finalSortIndbyX]
		finalBot = np.array(finalBot)
		
		return finalBot

	def getHigherEdgePoints(self,corners):
		arr = np.array(corners)
		if arr.shape[0] < 40:
			return []

		arr = arr.reshape(arr.shape[0],2)
		sortInd = np.lexsort((arr[:,1],arr[:,0]))
		higherCorners = arr[sortInd]

		finalTop = []
		for foo in range(0,10):
			packet = [higherCorners[foo*4],higherCorners[foo*4+1],higherCorners[foo*4+2],higherCorners[foo*4+3]]
			packet = np.array(packet)

			top2Ind = np.lexsort((packet[:,0],packet[:,1]))[:-2]
			finalTop.append(packet[top2Ind[0]])
			finalTop.append(packet[top2Ind[1]])

		finalTop = np.array(finalTop)
		sortInd = np.lexsort((finalTop[:,1],finalTop[:,0]))
		finalTop = finalTop[sortInd]
		finalTop = np.array(finalTop)
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
