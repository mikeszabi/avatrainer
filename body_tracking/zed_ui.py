import threading
import queue

import datetime
import PIL
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import font
import argparse
import datetime
import cv2
import os
import zed_wrapper



class ZED_video_player:
    def __init__(self, output_dir = "../store"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """

        self.left_queue=None
        self.right_queue=None

        # self.vs = cv2.VideoCapture('Kaabil Hoon (Kaabil) Hrithik Roshan (2K Ultra HD 1440p)-(HDLoft.Com).mp4') # capture video frames, 0 is your default video camera
        self.output_dir = output_dir  # store output path
        # self.current_image = None  # current image from the camera
        # self.thread = None
        # self.stopEvent = None
        # self.rt_frame_counter=0
        # self.rt_time_counter=0
        self.t_rec_start=None
        # self.frame_counter=0



        self.root = tk.Tk()  # initialize root window
        self.root.title("Avatrainer")  # set window title

        self.root.config(cursor="arrow",bg='lightgray')
        
        self.zb=zed_wrapper.ZED_body()
        # self.zed_connect()
        
        
        # if self.zb is None:
        #     self.onAppClose()
        self.disp_width=self.zb.display_resolution.width
        self.disp_height=self.zb.display_resolution.height
               
        self.gui_layout()
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onAppClose)

        # start video loop
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.main_loop, args=())
        self.thread.start()       
        
        self.root.mainloop()

        
    def gui_layout(self):
        # Create real time image window
        test_image=ImageTk.PhotoImage(Image.open(r"../assets/personal_trainer.jpg").resize((self.disp_width,self.disp_height)))

        self.btn_live = tk.Button(self.root, text="LIVE", bg='gray', command=self.OnLive)
        self.btn_live.grid(row=1, column=1)
        
        self.btn_playback_left = tk.Button(self.root, text="PLAYBACK", bg='gray', command=self.OnPlaybackLeft)
        self.btn_playback_left.grid(row=1, column=2)
        
        self.btn_playback_right = tk.Button(self.root, text="PLAYBACK", bg='gray', command=self.OnPlaybackRight)
        self.btn_playback_right.grid(row=1, column=4)

        # VIDEO PANELS
        self.right_panel = tk.Label(self.root,image=test_image,width=self.disp_width, height=self.disp_height)
        self.right_panel.image = test_image#,width=640, height=364)  # initialize image panel
        self.right_panel.grid(row=2, column=1, padx=5, pady=5, columnspan=2)

        self.left_panel = tk.Label(self.root,image=test_image,width=self.disp_width, height=self.disp_height)
        self.left_panel.image = test_image#,width=640, height=364)  # initialize image panel
        #self.right_panel.pack(side="right", padx=10, pady=10)
        self.left_panel.grid(row=2, column=3, padx=5, pady=5, columnspan=2)
        
        self.btn_record = tk.Button(self.root, text="Record", bg='gray', command=self.OnRecord)
        self.btn_record.grid(row=3, column=2)
        
        self.rt_timer = tk.Label(self.root, height = 2, width = 30)
        self.rt_timer.grid(row=3, column=1)
        
        self.rt_save_instruction=tk.Label(self.root,text="SVO FILE NAME:",height = 1,width = 20,font=font.Font(family = "Open look cursor", size = 10))
        self.rt_save_instruction.grid(row=4, column=1)
        
        self.rt_save_file=tk.Text(self.root,height = 1,width = 30,font=font.Font(family = "Open look cursor", size = 10))
        self.rt_save_file.grid(row=4,column=2)
        
        self.btn_starstop = tk.Button(self.root, text="Start", command=self.OnStartStop)
        self.btn_starstop.grid(row=3, column=3, rowspan=6)
        
        self.rec_timer = tk.Label(self.root, height = 2, width = 30)
        self.rec_timer.grid(row=3, column=4)
        
        self.file_list_box=tk.Listbox(self.root,width=100,font=font.Font(family = "Open look cursor", size = 8))
        self.file_list_box.grid(row=4,column=3,columnspan=2)
        self.RefreshFileList()

   

    def main_loop(self):
        """ Get frame from the video stream and show it in Tkinter """

        # left_queue = queue.Queue()
        # thread_1 = threading.Thread(target=self.zb.live, args=((left_queue,)))
        # thread_1.start()     
        

        try:
            while not self.stopEvent.is_set():
                #if left_live:
                if self.left_queue is not None:
                    #print(f'live images in queue:{self.left_queue.qsize()}')
                    live_frame=None
                    while not self.left_queue.empty():
                        live_frame=self.left_queue.get()
                    if live_frame is not None:
                        frame_counter_live=live_frame['position']
                        if self.t_rec_start is not None:
                            delta=datetime.datetime.now()-self.t_rec_start
                            self.rt_timer.config(text=f"{str(frame_counter_live)} : {str(delta.total_seconds())}")
                        current_image=live_frame['image_left_live_ocv']
                        current_image=cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        
                        imgtk=ImageTk.PhotoImage(image=Image.fromarray(current_image).resize((self.disp_width,self.disp_height)))
                        self.right_panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
                        self.right_panel.config(image=imgtk)  # show the image
                        self.root.update()
                if self.right_queue is not None:
                    playback_frame=None
                    while not self.right_queue.empty():
                        playback_frame=self.right_queue.get()
                    if playback_frame is not None:
                        # frame_counter_playback=playback_frame['position']
                        # if self.t_rec_start is not None:
                        #     delta=datetime.datetime.now()-self.t_rec_start
                        #     self.rt_timer.config(text=f"{str(frame_counter_live)} : {str(delta.total_seconds())}")
                        current_image=playback_frame['image_left_playback_ocv']
                        current_image=cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        
                        imgtk=ImageTk.PhotoImage(image=Image.fromarray(current_image).resize((self.disp_width,self.disp_height)))
                        self.left_panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
                        self.left_panel.config(image=imgtk)  # show the image
                        self.root.update()

        except RuntimeError:
            print("[INFO] caught a RuntimeError")
            
    def OnPlaybackRight(self):
        print('left')
        if self.zb.playbackOn_right.is_set():
            self.zb.paybackOn_right.clear()
            self.right_queue=None
            self.btn_playback_right.config(bg='gray')
        else:
            selected_file_index = self.file_list_box.curselection()[0]
            print(self.file_list_box.get(selected_file_index))
            file_name=os.path.join(self.output_dir,self.file_list_box.get(selected_file_index))
            if len(file_name):
                self.zb.playbackOn_right.set()
                self.right_queue = queue.Queue()
                thread = threading.Thread(target=self.zb.playback, args=((self.right_queue,file_name)))
                thread.start()     
                self.btn_playback_right.config(bg='red')
            else:
                print("[INFO] file name is not set")
        
    def OnPlaybackLeft(self):
        print('right')
        


    def OnRecord(self):
        
        if self.zb.liveOn.is_set():
            if self.zb.liveRec.is_set():
                # STOP RECORDING
                self.zb.liveRec.clear()
                self.t_rec_start=None
                self.btn_record.config(bg='green')
            else:
                # START RECORDING
                self.zb.liveRec.set()
                self.t_rec_start=datetime.datetime.now()
                self.btn_record.config(bg='red')
        else:
            self.btn_record.config(bg='gray')    
            
        
    def OnLive(self):
        if self.zb.liveOn.is_set():
            self.zb.liveOn.clear()
            self.left_queue=None
            self.btn_live.config(bg='gray',text="START LIVE")
        else:
            # start live loop
            file_name=self.rt_save_file.get('1.0','end-1c')
            if len(file_name):
                self.zb.liveOn.set()
                self.left_queue = queue.Queue()
                file_name+='_'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+'.svo'
                print("[INFO] saved {}".format(file_name))
                thread = threading.Thread(target=self.zb.live, args=((self.left_queue,file_name)))
                thread.start()     
                self.btn_live.config(bg='red',text="STOP LIVE")
            else:
                print("[INFO] file name is not set")
            
        
    def OnStartStop(self):
        # grab the current timestamp and use it to construct the
        # output path
        # ts = datetime.datetime.now()
        selected_file_index = self.file_list_box.curselection()[0]
        print(self.file_list_box.get(selected_file_index))
        # self.zb.playback(os.path.join(self.output_dir,self.file_list_box.get(selected_file_index)))
        # filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        # filepath = os.path.sep.join((self.outputPath, filename))
        # # save the file
        # self.wci.saveStereoImage(filepath,self.isDetectionOn)
        # #self.wci.saveImage(filepath)
        # print("[INFO] saved {}".format(ts))
        
    def RefreshFileList(self):
        myList = os.listdir(r'../store')
        print(myList)
        self.file_list_box.delete(0, tk.END)
        for file in myList:
            self.file_list_box.insert(tk.END, file)
        
    def onAppClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        # if self.stopEvent is not None:
        #     self.stopEvent.set()
        self.root.destroy()
