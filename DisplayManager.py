import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
from ImageTaker import ImageTaker
from Analyser import Analyser

	
class DisplayManager(object):
	def __init__(self,cam):
		self.cam = cam

	def printROI(self):
		r = cv2.selectROI(self.cam.raw)
		#print(r)
		x1 = r[0]
		y1 = r[1]
		x2 = r[0]+r[2]
		y2 = r[1] +r[3]
		print(x1,y1,x2,y2)
		print(y1,y2, x1,x2)
		#print(imCrop.mean())

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
		Copy = self.cam.raw.copy()
		mainCopy = self.cam.cropROI(self.cam.mainZone,Copy)
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
	def displayDebug(self):
		img = self.cam.raw.copy()
		self.addROIRectangles(img)
		cv2.imshow('Debug',img)		

	def drawRectangleOverROI(self,ROI,img):
		cv2.rectangle(img,(ROI[0],ROI[1]),(ROI[2],ROI[3]),(0,255,0),3)

	def drawErrorRectangleOverROI(self,ROI,img):
		cv2.rectangle(img,(ROI[0],ROI[1]),(ROI[2],ROI[3]),(0,0,255),3)

	def displayBinary(self):
		bw_img = self.cam.binaryPin.copy()
		cv2.imshow('Binary', bw_img)
	def drawContourBoxes(self,img):
		
		pass
if __name__ == "__main__":
	print("starting camera")
	foo = ImageTaker()
	display = DisplayManager(foo)
	print("starting Display")
	while True:
		foo.captureBinarizePinsAndLettering()
		foo.cropOutAllZonesinColor()
		#raw = display.addROIRectangles()
		display.displayDebug()
		display.displayBinary()
		#raw = foo.raw
		cropped = foo.main
		cropcrop = foo.topPinRow
		#cv2.imshow('rectangle',raw)
		cv2.imshow('raw',foo.raw)
		#cv2.imshow('crop of crop', cropcrop)
		cv2.waitKey(1)

	foo.cap.stream.release()
	cv2.destroyAllWindows()
