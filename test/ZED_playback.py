#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 08:44:29 2023

@author: itqs
"""


import sys
import pyzed.sl as sl
import threading

input_path = r'../store/test.svo' #sys.argv[0]


# Create a ZED camera object
# Set SVO path for playback
init_1 = sl.InitParameters()
init_1.set_from_svo_file(r'../store/test.svo')

svo_file=r'../store/a1_2023_06_21_10_52_36.svo'


init_2 = sl.InitParameters()
init_2.set_from_svo_file(svo_file)
init_2.camera_fps=15


def zed_playback_loop(init):
    zed1 = sl.Camera()
    status = zed1.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    exit_app=False
    svo_image = sl.Mat()
    while not exit_app:
      if zed1.grab() == sl.ERROR_CODE.SUCCESS:
          print(f"fps: {zed1.get_current_fps()}")
          # Read side by side frames stored in the SVO
          zed1.retrieve_image(svo_image, sl.VIEW.SIDE_BY_SIDE)
          # Get frame count
          svo_position = zed1.get_svo_position();
      elif zed1.grab() == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
          print("SVO end has been reached. Looping back to first frame")
          zed1.set_svo_position(0)
          exit_app=True


stopEvent = threading.Event()
thread_1 = threading.Thread(target=zed_playback_loop, args=(init_1,))
thread_1.start()     

thread_2 = threading.Thread(target=zed_playback_loop, args=(init_2,))
thread_2.start()       
  

