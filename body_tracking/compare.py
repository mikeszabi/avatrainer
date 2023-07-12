#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:38:16 2023

@author: itqs
"""

import sys
sys.path.append(r'../measure')
import threading
import queue
import zed_wrapper
from oks import oks
# from bones import run
from cv_viewer.utils import *
import cv_viewer.tracking_viewer as cv_viewer

import pyzed.sl as sl
import cv2
import numpy as np
from matplotlib import pyplot as plt

filepath_1=r'../store/kitores_oldal_1_2023_06_23_11_08_58_cut.svo'
filepath_2=r'../store/kitores_oldal_2_2023_06_23_11_09_27_cut.svo'

step_by_step=5

thread_left=threading.Thread()
thread_right=threading.Thread()
queue_left = queue.Queue()
queue_right = queue.Queue()

liveEvent_left = threading.Event()
recordEvent_left = threading.Event()
  
playbackEvent_left = threading.Event()
playbackEvent_right = threading.Event()
  
playbackStartEvent_left = threading.Event()
playbackStartEvent_right = threading.Event()
  

  
zb_left=zed_wrapper.ZED_body()
zb_right=zed_wrapper.ZED_body()

playbackEvent_left.set()
playbackStartEvent_left.clear()
thread_left = threading.Thread(target=zb_left.playback, args=((queue_left,playbackEvent_left,playbackStartEvent_left,
                                                               filepath_1,step_by_step,False)))

playbackEvent_right.set()
playbackStartEvent_right.clear()
thread_right = threading.Thread(target=zb_right.playback, args=((queue_right,playbackEvent_right,playbackStartEvent_right,
                                                               filepath_2,step_by_step,False)))

thread_left.start()  
thread_right.start()

    
imdat_left=None
imdat_right=None
bodies_obj_list_left=[]
bodies_obj_list_right=[]
svo_pos_left=step_by_step
svo_pos_right=step_by_step


im_h = cv2.imread(r"../assets/personal_trainer.jpg", cv2.IMREAD_COLOR)
scale_percent = 50 # percent of original size
width = int(im_h.shape[1] * scale_percent / 100)
height = int(im_h.shape[0] * scale_percent / 100)
dim = (width, height)
  
# resize image
im_h = cv2.resize(im_h, dim, interpolation = cv2.INTER_AREA)
 
im_h = cv2.hconcat([im_h, im_h])

key=0
while key != 27:  # for esc

    
    if queue_left.qsize()>0:
        imdat_left=queue_left.get()
    else:
        imdat_left=None
    if queue_right.qsize()>0:    
        imdat_right=queue_right.get()
    else:
        imdat_right=None
    

    if imdat_left is not None:
        bodies_obj_list_left=imdat_left['bodypoints']
        image_left_playback_ocv=imdat_left['image_ocv']
        svo_pos_left=imdat_left['position']
    if imdat_right is not None:
        bodies_obj_list_right=imdat_right['bodypoints']
        image_right_playback_ocv=imdat_right['image_ocv']
        svo_pos_right=imdat_right['position']

        
    if len(bodies_obj_list_left)>0 and len(bodies_obj_list_right)>0:
        
        # bodies_obj_list[0].keypoint[sl.BODY_PARTS.LEFT_HIP.value]
        
        cv_viewer.render_2D(image_left_playback_ocv,zb_left.image_scale,bodies_obj_list_left, zb_left.obj_param.enable_tracking, zb_left.obj_param.body_format)
        cv_viewer.render_2D(image_right_playback_ocv,zb_right.image_scale,bodies_obj_list_right, zb_right.obj_param.enable_tracking, zb_right.obj_param.body_format)
        image_left_playback_ocv=cv2.putText(image_left_playback_ocv, str(svo_pos_left), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
        image_right_playback_ocv=cv2.putText(image_right_playback_ocv, str(svo_pos_right), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
       
        ###
        obj_left=bodies_obj_list_left[0]
        # run(obj_left)
        obj_right=bodies_obj_list_right[0]
        
        visibility=np.isnan(np.sum(obj_left.keypoint,axis=1))*np.isnan(np.sum(obj_right.keypoint,axis=1))==0
        
        obj_key_score=oks(obj_left.keypoint, obj_right.keypoint, visibility)
        print("OKS", obj_key_score)
        

        im_h = cv2.hconcat([image_left_playback_ocv, image_right_playback_ocv])
        if obj_key_score>0.9925:
            color=(0,255,0)
        else:
            color=(0,0,255)
        im_h = cv2.putText(im_h, "{0:.3f}".format(obj_key_score), (100,30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
        # im_h=cv2.cvtColor(im_h, cv2.COLOR_BGR2RGB)
        
        
    ###
    
      
    if key == 97 or key==115: #a / s
        playbackStartEvent_left.set()
    if key == 100 or key==115: #d / s
        playbackStartEvent_right.set()    

    
    cv2.imshow("ZED | 2D View", im_h)
    key=cv2.waitKey(0)

    
    
playbackEvent_left.clear()
playbackEvent_right.clear()