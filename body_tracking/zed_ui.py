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


# ToDO: self.playbackOn - alternate
# Vagy live + playback megy, vagy playback + playback

class ZED_video_player:
    def __init__(self, output_dir = "../store"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """


        self.thread_left=threading.Thread()
        self.thread_right=threading.Thread()
        self.queue_left = queue.Queue()
        self.queue_right = queue.Queue()

        self.liveEvent_left = threading.Event()
        self.recordEvent_left = threading.Event()
        
        self.playbackEvent_left = threading.Event()
        self.playbackEvent_right = threading.Event()
        
        self.playbackStartEvent_left = threading.Event()
        self.playbackStartEvent_right = threading.Event()
        
        self.mainstopEvent = threading.Event()

        # self.vs = cv2.VideoCapture('Kaabil Hoon (Kaabil) Hrithik Roshan (2K Ultra HD 1440p)-(HDLoft.Com).mp4') # capture video frames, 0 is your default video camera
        self.output_dir = output_dir  # store output path
        # self.current_image = None  # current image from the camera
        # self.thread = None
        # self.mainstopEvent = None
        # self.rt_frame_counter=0
        # self.rt_time_counter=0
        self.t_left_start=None
        self.t_right_start=None


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
        
        self.thread = threading.Thread(target=self.main_loop, args=(self.mainstopEvent,))
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
        self.right_panel.grid(row=2, column=3, padx=5, pady=5, columnspan=2)

        self.left_panel = tk.Label(self.root,image=test_image,width=self.disp_width, height=self.disp_height)
        self.left_panel.image = test_image#,width=640, height=364)  # initialize image panel
        self.left_panel.grid(row=2, column=1, padx=5, pady=5, columnspan=2)
        
        self.right_fn = tk.Label(self.root,text='---')
        self.right_fn.grid(row=2, column=3, padx=5, pady=5)
        
        self.left_fn = tk.Label(self.root,text='---')
        self.left_fn.grid(row=2, column=1, padx=5, pady=5)
        
        # BUTTONS
        
        self.btn_record = tk.Button(self.root, text="Record", bg='gray', command=self.OnRecord)
        self.btn_record.grid(row=3, column=2)
        
        self.left_timer = tk.Label(self.root, height = 2, width = 30)
        self.left_timer.grid(row=3, column=1)
        
        self.right_timer = tk.Label(self.root, height = 2, width = 30)
        self.right_timer.grid(row=3, column=4)
        
        self.rt_save_instruction=tk.Label(self.root,text="SVO FILE NAME:",height = 1,width = 20,font=font.Font(family = "Open look cursor", size = 10))
        self.rt_save_instruction.grid(row=4, column=1)
        
        self.rt_save_file=tk.Text(self.root,height = 1,width = 30,font=font.Font(family = "Open look cursor", size = 10))
        self.rt_save_file.grid(row=4,column=2)
        
        self.btn_starstop_left = tk.Button(self.root, text="START", command=self.OnStartStopLEFT)
        self.btn_starstop_left.grid(row=3, column=3)
        
        
        self.file_list_box=tk.Listbox(self.root,width=100,font=font.Font(family = "Open look cursor", size = 8))
        self.file_list_box.grid(row=4,column=3,columnspan=2)
        self.file_list_box.bind("<<ListboxSelect>>", self.OnFileSelect)
        self.RefreshFileList()

   

    def main_loop(self,mainstopEvent):
        """ Get frame from the video stream and show it in Tkinter """

        # queue_left = queue.Queue()
        # thread_1 = threading.Thread(target=self.zb.live, args=((queue_left,)))
        # thread_1.start()     
        

        try:
            while not mainstopEvent.is_set():
                #if left_live:
                if self.thread_left.is_alive():
                    # print(f'live images in queue:{self.queue_left.qsize()}')
                    left_frame=None
                    while not self.queue_left.empty():
                        left_frame=self.queue_left.get()
                    if left_frame is not None:
                        frame_counter_left=left_frame['position']
                        if self.t_left_start is not None:
                            delta=datetime.datetime.now()-self.t_left_start
                            self.left_timer.config(text=f"{str(frame_counter_left)} : {str(delta.total_seconds())}")
                        current_image=left_frame['image_ocv']
                        current_image=cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        
                        imgtk=ImageTk.PhotoImage(image=Image.fromarray(current_image).resize((self.disp_width,self.disp_height)))
                        self.left_panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
                        self.left_panel.config(image=imgtk)  # show the image
                        self.root.update()
                    else:
                        print('left queue is None')
                    self.btn_playback_left.config(bg='red')
                else:
                    self.btn_playback_left.config(bg='green')
                        
                if self.thread_right.is_alive():
                    # print(f'images in queue:{self.queue_right.qsize()}')

                    right_frame=None
                    while not self.queue_right.empty():
                        right_frame=self.queue_right.get()
                    if right_frame is not None:
                        frame_counter_right=right_frame['position']
                        if self.t_right_start is not None:
                            delta=datetime.datetime.now()-self.t_right_start
                            self.right_timer.config(text=f"{str(frame_counter_right)} : {str(delta.total_seconds())}")
                        current_image=right_frame['image_ocv']
                        current_image=cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        
                        imgtk=ImageTk.PhotoImage(image=Image.fromarray(current_image).resize((self.disp_width,self.disp_height)))
                        self.right_panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector  
                        self.right_panel.config(image=imgtk)  # show the image
                        self.root.update()
                    else:
                        print('right queue is None')
                        
                #self.RefreshFileList()

        except RuntimeError:
            print("[INFO] caught a RuntimeError")
            
    def OnPlaybackRight(self):
        print('right')
        if not self.playbackEvent_right.is_set():
            if not self.thread_right.is_alive(): 
          
                selected_file_index = self.file_list_box.curselection()[0]
                print(self.file_list_box.get(selected_file_index))
                file_name=os.path.join(self.output_dir,self.file_list_box.get(selected_file_index))
                
                if len(file_name):
                    self.right_fn.config(text=file_name)
                    # PLAYBACK THREAD STARTS
                    self.playbackEvent_right.set()
                    self.playbackStartEvent_right.clear()
                    self.thread_right = threading.Thread(target=self.zb.playback, args=((self.queue_right,
                                                                                         self.playbackEvent_right,
                                                                                         self.playbackStartEvent_right,
                                                                                         file_name)))
                    self.thread_right.start()     
                    self.btn_playback_right.config(bg='red')
                else:
                    self.right_fn.config(text='---')
                    print("[INFO] file name is not set")
                    self.btn_playback_right.config(bg='red')
            else:
                self.btn_playback_right.config(bg='red')
        else:
            self.right_fn.config(text='---')
            self.playbackEvent_right.clear()
            self.playbackStartEvent_right.clear()
            self.btn_playback_right.config(bg='green')
         
        
    def OnPlaybackLeft(self):
        print('left')
        if not self.playbackEvent_left.is_set():
            if not self.thread_left.is_alive():
                    
                selected_file_index = self.file_list_box.curselection()[0]
                print(self.file_list_box.get(selected_file_index))
                file_name=os.path.join(self.output_dir,self.file_list_box.get(selected_file_index))
                
                if len(file_name):
                    self.left_fn.config(text=file_name)
                    # PLAYBACK THREAD STARTS
                    self.playbackEvent_left.set()
                    self.playbackStartEvent_left.clear()
                    self.thread_left = threading.Thread(target=self.zb.playback, args=((self.queue_left,
                                                                                         self.playbackEvent_left,
                                                                                         self.playbackStartEvent_left,
                                                                                         file_name)))
                    self.thread_left.start()   
                    self.btn_playback_left.config(bg='gray')
                else:
                    self.left_fn.config(text='---')
                    print("[INFO] file name is not set")
                    self.btn_playback_left.config(bg='red')
            else:
                self.btn_playback_left.config(bg='red')
                
        else:
            self.left_fn.config(text='---')
            self.playbackEvent_left.clear()
            self.playbackStartEvent_left.clear()
            self.btn_playback_left.config(bg='green')
            
                    
    def OnLive(self):
        
        if not self.liveEvent_left.is_set():
            if not self.thread_left.is_alive():
                file_name=self.rt_save_file.get('1.0','end-1c')
                
                if len(file_name):
                    self.left_fn.config(text=file_name)
                    # LIVE THREAD STARTS
                    self.liveEvent_left.set()
                    self.recordEvent_left.clear()
                    file_name+='_'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+'.svo'
                    print("[INFO] saved {}".format(file_name))
                    self.thread_left = threading.Thread(target=self.zb.live, args=((self.queue_left,
                                                                                    self.liveEvent_left,
                                                                                    self.recordEvent_left,
                                                                                    file_name)))
                    self.thread_left.start()     
                    self.btn_live.config(bg='red')
                else:
                    self.left_fn.config(text='---')
                    print("[INFO] file name is not set")
                    self.btn_live.config(bg='red')
            else:
                self.btn_live.config(bg='red')
        else:
            self.left_fn.config(text='---')
            self.liveEvent_left.clear()
            self.recordEvent_left.clear()
            self.btn_live.config(bg='green')
    
    def OnRecord(self):
        
        if self.liveEvent_left.is_set():
            if self.recordEvent_left.is_set():
                # STOP RECORDING
                self.recordEvent_left.clear()
                self.t_left_start=None
                self.btn_record.config(bg='green')
            else:
                # START RECORDING
                self.recordEvent_left.set()
                self.t_left_start=datetime.datetime.now()
                self.btn_record.config(bg='red')
        else:
            self.btn_record.config(bg='gray')                
        
    def OnStartStopLEFT(self):
        if self.playbackEvent_right.is_set():
            if not self.playbackStartEvent_right.is_set():
                # start video
                self.playbackStartEvent_right.set()
                self.t_right_start=datetime.datetime.now()
                self.btn_starstop_left.config(bg='red',text="STOP")
    
            else:
                self.playbackStartEvent_right.clear()
                self.t_right_start=None
                self.btn_starstop_left.config(bg='green',text="START")
        else:
            self.btn_starstop_left.config(bg='gray',text="START")
            
        
        if not self.liveEvent_left.is_set():
            if self.playbackEvent_left.is_set():
                if not self.playbackStartEvent_left.is_set():
                    # start video
                    self.playbackStartEvent_left.set()
                    self.t_left_start=datetime.datetime.now()        
                else:
                    self.playbackStartEvent_left.clear()
                    self.t_left_start=None
            else:            
                self.t_left_start=None

        
    def RefreshFileList(self):
        myList = os.listdir(r'../store')
        # print(myList)
        self.file_list_box.delete(0, tk.END)
        for file in myList:
            self.file_list_box.insert(tk.END, file)
            
    def OnFileSelect(self,event):
        self.btn_playback_right.config(bg='green')
        
        
    def onAppClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        self.mainstopEvent.set()
        print("[INFO] closing...")
        # if self.mainstopEvent is not None:
        #     self.mainstopEvent.set()
        self.root.destroy()
