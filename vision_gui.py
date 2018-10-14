#/usr/bin/python

from Tkinter import *
import cv2
from gpiozero import OutputDevice,InputDevice
import time

from ImageAnalyse import Analyser
from ImageCapture import ImageCapture
from DisplayManager import DisplayManager
from QA_control import QA_control
from Ismeca_interface import Ismeca_int


class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)                 
		self.master = master
		self.init_window()
    #Creation of init_window
	def init_window(self):
		self.master.title("Comport Vision System")
		self.pack(fill=BOTH, expand=1)
		self.w=Canvas(self.master, width=400,height=50)
		self.w.pack()
		self.w.create_rectangle(5,0,395,50,fill="green")
		quitButton = Button(self, text="Exit",command=self.client_exit,fg="red",width=10,height=2)
		quitButton.place(x=0, y=109)
		RecheckButton = Button(self, text="Recheck",command=self.client_recheck,width=10,height=2)
		RecheckButton.place(x=0, y=10)
 		resetButton = Button(self, text="Skip",command=self.client_skip,width=10,height=2)
		resetButton.place(x=0, y=60)      
		Label(self, text="Pass").place(x=300,y=20)
		Label(self,textvariable=pass_dev).place(x=250,y=20)
		Label(self, text="Fail").place(x=300,y=70)
		Label(self,textvariable=fail_dev).place(x=250,y=70)
		Label(self, text="Total").place(x=300,y=120)
		Label(self,textvariable=total_dev).place(x=250,y=120)
		self.field_update()


	def field_update(self):
		pass_dev.set(main.dpass)
		fail_dev.set(main.dfail)
		total_dev.set(main.total)

	def client_exit(self):
		main.exit=True
		exit(0)

	def client_recheck(self):
		main.recheck=True

	def client_skip(self):
		main.skip=True

	def client_reset(self):
		main.dpass=0
		main.dfail=0
		main.total=0
		main.lead_trail_cnt=5

main=Ismeca_int()
root = Tk()
pass_dev=StringVar()
fail_dev=StringVar()
total_dev=StringVar()
root.geometry("400x200")
#creation of an instance
app = Window(root)
i=0;
while 1:
	main.ismeca_ctrl()
	if i>5:
		root.update_idletasks()
		root.update()
		app.field_update()
		if main.status ==0:
			app.w.create_rectangle(5,0,395,50,fill="green")
		elif main.status==1:
			app.w.create_rectangle(5,0,395,50,fill="black")
		elif main.status==2:
			app.w.create_rectangle(5,0,395,50,fill="yellow")	
		else:
			app.w.create_rectangle(5,0,395,50,fill="red")
		i=0
	else:
		i=i+1
	time.sleep(0.005)

