import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
from imutils.video import FPS
from imutils.video import WebcamVideoStream
import imutils

vs = WebcamVideoStream(src=0).start()
frame = vs.read()
cv2.imshow("Frame", frame)
while True:
 
	# check to see if the frame should be displayed to our screen
	if False:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# update the FPS counter
	if cv2.waitKey(1) & 0xFF == ord('q'):
		frame = vs.read()
		rectangleFrame = frame.copy()
		circleFrame = frame.copy()
		
		cv2.imshow("Original", frame)

		cv2.rectangle(rectangleFrame,(384,0),(510,128),(0,255,0),3)
		cv2.imshow("Capture", rectangleFrame)
		cv2.waitKey(1000)

		cv2.circle(circleFrame,(447,63), 63, (0,0,255), -1)
		cv2.imshow("lel", circleFrame)
		cv2.waitKey(1000)
vs.release()
cv2.destroyAllWindows()
	
 
