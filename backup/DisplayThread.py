# import the necessary packages
import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
from threading import Thread
import cv2
from imutils.video import WebcamVideoStream
import time

class DisplayThread:
	def __init__(self, name="Display Timer"):
		# initialize the thread name
		self.name = name
	
		# initialize the flag variables
		self.stopped = False
		self.resetFlag = False
		self.showimage = False
	def start(self):

		# start the thread to read frames from the video stream
		t = Thread(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()

		return self
	def show(self):
		img  = self.cam.read()
		cv2.imshow('DisplayThread',img)
		cv2.waitKey(1)
		
	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			#resetting flag
			self.resetFlag = False
			
			time.sleep(1)
			self.showimage = True
			while not self.resetFlag:
				time.sleep(0.01)
	
	def reset(self):
		#Resetting Flag variables
		self.resetFlag = True
		self.showimage = False
	
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

if __name__ == "__main__":
	print("starting camera")
	foo = WebcamVideoStream(src = 0).start()
	print("starting Display")
	display = DisplayThread()
	display.start()
	while True:
		if display.showimage:
			img = foo.read()
			cv2.imshow('raw', img)
			cv2.waitKey(1)
			display.reset()
	
	foo.stop()
	foo.stream.release()
	cv2.destroyAllWindows()
