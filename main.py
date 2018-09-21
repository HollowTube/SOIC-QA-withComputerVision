from gpiozero import Button,OutputDevice,InputDevice
import time
from ImageAnalyse import Analyser
from ImageCapture import ImageCapture
from DisplayManager import DisplayManager
from QA_control import QA_control
import cv2


if __name__ == "__main__":
	print("Initializing...")
	cam = ImageTaker()
	scanner = Scanner(cam)
	on = OutputDevice(22)
	trigger = InputDevice(4)
	busy = OutputDevice(27)
	failFlag = OutputDevice(17)
	on.on()
	time.sleep(1)
	devOffset=5
	dpass=0
	dfail=0
	total=0
	print("Complete")
	while True:
		print("Waiting for Trigger")
		
		while trigger.value is True:
			time.sleep(0.010)
		start_time = time.time()
		failFlag.on()
		time.sleep(0.45)
		# Turn busy on, t
		busy.on()
		total=total+1
	    	good = scanner.fullScan()
	   	end_time = time.time()
		print("time taken {0}".format(end_time-start_time))
	    	if good is False and total > devOffset	:
			failFlag.on()
			dfail=dfail+1
			print("----------FAIL----------")
	    	else:
			failFlag.off()
			dpass=dpass+1
			print("+++++PASS+++++")
		# Test done
		busy.off()
		print "Currrent test %d      Total Pass: %d Total Fail: %d"  % (good,dpass,dfail)
		# Wait until the trigger is released
	    	while trigger.value is False:
			time.sleep(0.01)
		
	cv2.destroyAllWindows()

