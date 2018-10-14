#!/usr/bin/python
from gpiozero import Button,OutputDevice,InputDevice
import time
from ImageAnalyse import Analyser
from ImageCapture import ImageCapture
from DisplayManager import DisplayManager
from QA_control import QA_control
import cv2

class Ismeca_int(object):

	def __init__(self):
		print("Initializing...")
		self.cam = ImageCapture()
		self.scan = QA_control(self.cam)
		self.scan.debug=False
		self.ready = OutputDevice(22)
		self.trigger = InputDevice(4)
		self.busy = OutputDevice(27)
		self.failFlag = OutputDevice(17)
		self.ready.on()
		self.devOffset=5
		self.dpass=0
		self.dfail=0
		self.total=0
		self.lead_trail=True
		self.lead_trail_cnt=5
		self.debug=False
		self.exit=False
		self.triggered=True
		self.recheck=False
		self.status=0
		self.dev_check=0
		self.skip=False
		print("Ready")

	def device_check(self):
		self.busy.on()
		# When in leader or trailler mode, do not active the pick head disable function
		if self.lead_trail is False:
			self.failFlag.on()
		else:
			self.failFlag.off()
			self.dpass=0
			self.dfail=0
			self.total=0
		# Capture and analyse image
		self.scan.fullScan()
	    	self.dev_check= self.scan.error_code
		
		# Count the number of consecutive fail device
		if self.dev_check !=0:
			self.lead_trail_cnt = self.lead_trail_cnt +1
		else:
			self.lead_trail_cnt=0
	
		# If the consecutive fail is greater than devOffset enter lead_trail mode
		if self.lead_trail_cnt > self.devOffset:
			self.lead_trail= True
			# Destroy all window to clean up memory ????
			#cv2.destroyAllWindows()
		else:
			self.lead_trail=False

		# if not in lead_trail mode 
		if self.lead_trail is False:
	    		if self.dev_check ==0:
				self.failFlag.off()
				self.dpass=self.dpass+1
				self.status=0					
			elif self.scan.fullScan() is True :
				self.failFlag.off()
				self.dpass = self.dpass+1
				self.status=0
			else:
				self.failFlag.on()
				self.dfail =self.dfail+1
				self.status=3
			self.total += 1
		else:
			self.failFlag.off()
		self.busy.off()

	def ismeca_ctrl(self):
		# If exit the quit
		if self.exit is True:
			cv2.destroyAllWindows()
			exit(0)
		if self.skip is True:
			self.failFlag.off()
			self.status=0
			self.skip=False

		if self.recheck is True:
			start_time = time.time()	
			self.device_check()	
			end_time = time.time()
			print("time taken %5.3f" %(end_time-start_time))
			self.recheck=False
			self.triggered=True
			return
		# If it is already triggered then return else continue
		if self.triggered is True:
			if self.trigger.value is True:
				self.triggered=False
				return
			else:
				return
		
		#Wait for trigger from Ismeca, two while loop to remove the glitch due to space between sprocket		
		if self.debug is False :
			while self.trigger.value is True :
				return
			time.sleep(0.01)
			while self.trigger.value is True :
				time.sleep(0.005)
		self.triggered=True
		# after trigger sleep for 320ms so the pick head will clear the Deadspot
		time.sleep(0.32)	
		self.failFlag.on()	
		start_time = time.time()	
		self.device_check()	
		end_time = time.time()
		print("time taken %5.3f" %(end_time-start_time))
		return

		
if __name__ == "__main__":
	print("Initializing...")
	main=Ismeca_int()
	main.debug=False
	while True:
		main.ismeca_ctrl()
	cv2.destroyAllWindows()

