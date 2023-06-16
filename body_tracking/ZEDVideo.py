import threading
import datetime
import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os
import ZEDutils

class ZED_video_player:
    def __init__(self, output_dir = "../store"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        # self.vs = cv2.VideoCapture('Kaabil Hoon (Kaabil) Hrithik Roshan (2K Ultra HD 1440p)-(HDLoft.Com).mp4') # capture video frames, 0 is your default video camera
        self.output_dir = output_dir  # store output path
        # self.current_image = None  # current image from the camera
        self.thread = None
        self.stopEvent = None
        self.frame_counter=0


        self.root = tk.Tk()  # initialize root window
        self.root.title("Avatrainer")  # set window title
        # self.destructor function gets fired when the window is closed
        #self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        
        self.root.config(cursor="arrow",bg='lightgray')
        
        self.zb=None
        self.zed_connect()
        if self.zb is None:
            self.onAppClose()
        self.disp_width=self.zb.display_resolution.width
        self.disp_height=self.zb.display_resolution.height
               
        self.gui_layout()
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onAppClose)

        # start video loop
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.video_display_loop, args=())
        self.thread.start()       
        
        self.root.mainloop()

        
    def gui_layout(self):
        # Create real time image window
        test_image=ImageTk.PhotoImage(Image.open(r"../assets/personal_trainer.jpg").resize((self.disp_width,self.disp_height)))

        self.rt_panel = tk.Label(image=test_image,width=self.disp_width, height=self.disp_height)
        self.rt_panel.image = test_image#,width=640, height=364)  # initialize image panel
        #self.rt_panel.pack(side="right", padx=10, pady=10)
        self.rt_panel.grid(row=1, column=1, padx=5, pady=5, columnspan=2)

        #self.rec_panel = tk.Label(self.root,image=test_image,width=640, height=364)  # initialize image panel
        #self.rec_panel.grid(row=1, column=2, rowspan=6, padx=5, pady=5)

        self.rec_panel = tk.Label(image=test_image,width=self.disp_width, height=self.disp_height)
        self.rec_panel.image = test_image#,width=640, height=364)  # initialize image panel
        #self.rt_panel.pack(side="right", padx=10, pady=10)
        self.rec_panel.grid(row=1, column=3, padx=5, pady=5, columnspan=2)
        
        self.btn_record = tk.Button(self.root, text="Record", bg='green', command=self.OnRecord)
        self.btn_record.grid(row=3, column=2)
        
        self.rt_timer = tk.Label(self.root, height = 2, width = 30)
        self.rt_timer.grid(row=3, column=1)
        
        self.btn_starstop = tk.Button(self.root, text="Start", command=self.OnStartStop)
        self.btn_starstop.grid(row=3, column=3, rowspan=6)
        
        self.rec_timer = tk.Label(self.root, height = 2, width = 30)
        self.rec_timer.grid(row=3, column=4)

        
    def zed_connect(self):
        self.zb=ZEDutils.ZED_body()
        
        

    def video_display_loop(self):
        """ Get frame from the video stream and show it in Tkinter """

        try:
            while not self.stopEvent.is_set():
                if self.zb is not None:
                    frame = self.zb.grab_image()
                    if frame is not None:  # frame captured without any errors
                        self.frame_counter+=1
                        self.rt_timer.config(text=str(self.frame_counter))
                        self.current_image=frame.copy()
                        self.current_image=cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        
                        imgtk=ImageTk.PhotoImage(image=Image.fromarray(self.current_image).resize((self.disp_width,self.disp_height)))
                        self.rt_panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
                        self.rt_panel.config(image=imgtk)  # show the image
                        #self.root.attributes("-fullscreen",True)
                    # self.root.after(1, self.video_loop)  # call the same function after 30 milliseconds
            #viewer.exit()
        except RuntimeError:
            print("[INFO] caught a RuntimeError")


    def OnRecord(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        # filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        # filepath = os.path.sep.join((self.outputPath, filename))
        # # save the file
        # self.wci.saveStereoImage(filepath,self.isDetectionOn)
        # #self.wci.saveImage(filepath)
        print("[INFO] saved {}".format(ts))
        if self.zb.isRecording:
            self.zb.record_end()
        else:
            self.zb.record_start()
            
        if self.zb.isRecording:
            self.btn_record.config(bg='red')
        else:
            self.btn_record.config(bg='green')
            
        
        
    def OnStartStop(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        # filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        # filepath = os.path.sep.join((self.outputPath, filename))
        # # save the file
        # self.wci.saveStereoImage(filepath,self.isDetectionOn)
        # #self.wci.saveImage(filepath)
        print("[INFO] saved {}".format(ts))
        
    def onAppClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        if self.stopEvent is not None:
            self.stopEvent.set()
        self.root.destroy()
