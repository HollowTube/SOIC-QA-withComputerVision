from __future__ import print_function
import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import numpy as np
import argparse
from imutils.video import FPS
from imutils.video import WebcamVideoStream
import imutils

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=1000,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())



# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
#vs = WebcamVideoStream(src=0).start()
vs = cv2.VideoCapture(0)
fps = FPS().start()

ret, frame = vs.read()
cv2.imshow("Frame", frame)
# loop over some frames...this time using the threaded stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	
	
 
	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# update the FPS counter
	fps.update()
	if cv2.waitKey(1) & 0xFF == ord('q'):
		ret, frame = vs.read()
		cv2.imshow("Capture", frame)
		cv2.waitKey(10)
	if cv2.waitKey(1) & 0xFF == ord('t'):
		break

vs.release()
vs = WebcamVideoStream(src=0).start()

while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	
	
 
	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

	# update the FPS counter
	fps.update()
	if cv2.waitKey(1) & 0xFF == ord('q'):
		frame = vs.read()
		cv2.imshow("Capture", frame)
		cv2.waitKey(10)
	
 
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

"""
while True:

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if cv2.waitKey(1) & 0xFF == ord('c'):
		ret, frame = cap.read()
		gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
		cv2.imshow('gray',gray) 
"""


