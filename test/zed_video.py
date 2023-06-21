#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 08:00:21 2023

@author: itqs
"""

import zed_ui

zp=zed_ui.ZED_video_player()


import queue
import threading

import zed_wrapper

zb=zed_wrapper.ZED_body()

live_queue = queue.Queue()

# zb.live(live_queue)

thread_1 = threading.Thread(target=zb.live, args=((live_queue,)))
thread_1.start()     

playback_queue = queue.Queue()
thread_2 = threading.Thread(target=zb.playback, args=(r'../store/test.svo',playback_queue,))
thread_2.start()   

# import pyzed.sl as sl
# zed = sl.Camera()
# # Open the camera
# print("Connecting ZED....")
# err = zed.open(init_params)
# if err != sl.ERROR_CODE.SUCCESS:
#     print("ZED is not connected")
#     camera_info=None    
# else:
#     print("ZED is connected")
#     camera_info = zed.get_camera_information()
# return camera_info
# zed.close()

import pyzed.sl as sl

svo_file=r'../store/a1_2023_06_21_10_52_36.svo'
init_params_playback = sl.InitParameters()
init_params_playback.set_from_svo_file(svo_file)
init_params_playback.camera_fps=15
init_params_playback.save('a')

input_t = sl.InputType()
input_t.set_from_svo_file(svo_file)
init_params_playback.input = input_t
 
