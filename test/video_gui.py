import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os
import ZEDutils

class Application:
    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        # self.vs = cv2.VideoCapture('Kaabil Hoon (Kaabil) Hrithik Roshan (2K Ultra HD 1440p)-(HDLoft.Com).mp4') # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera

        self.zb=ZEDutils.ZED_body()

        self.root = tk.Tk()  # initialize root window
        self.root.title("Avatrainer")  # set window title
        # self.destructor function gets fired when the window is closed
        #self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
        self.root.config(cursor="arrow")

        # create a button, that when pressed, will take the current frame and save it to file
        # btn = tk.Button(self.root, text="Record!", command=self.record)
        # btn.pack(fill="both", expand=True, padx=10, pady=10)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        frame = self.zb.grab_image()
#        frame = cv2.resize(frame, (1500,1000))
        print(frame)
        if frame is not None:  # frame captured without any errors
            # key = cv2.waitKey(1000)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            #self.current_image= self.current_image.resize([1280,1024],PIL.Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter 
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
            self.panel.config(image=imgtk)  # show the image
            #self.root.attributes("-fullscreen",True)
        self.root.after(1, self.video_loop)  # call the same function after 30 milliseconds

    # def record(self):
    #     """ Take snapshot and ...
