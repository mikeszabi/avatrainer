#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:38:16 2023

@author: itqs
"""

import threading
import queue
import zed_wrapper


filepath_1=r'../store/biceps_cur_1_2023_06_23_11_16_25_cut.svo'
filepath_2=r'../store/biceps_cur_2_2023_06_23_11_17_14_cut.svo'

step_by_step=10

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

if queue_left.qsize()>0:
    imdat_left=queue_left.get()
if queue_right.qsize()>0:    
    imdat_right=queue_right.get()

playbackStartEvent_left.set()
playbackStartEvent_right.set()




# playbackEvent_left.clear()
# playbackEvent_right.clear()

from cv_viewer.utils import *
import cv_viewer.tracking_viewer as cv_viewer

import pyzed.sl as sl
import cv2

bodies_obj_list_left=imdat_left['bodypoints']
image_left_playback_ocv=imdat_left['image_ocv']

bodies_obj_list_right=imdat_right['bodypoints']
image_right_playback_ocv=imdat_right['image_ocv']

# bodies_obj_list[0].keypoint[sl.BODY_PARTS.LEFT_HIP.value]

# cv_viewer.render_2D(image_left_playback_ocv,zb_left.image_scale,bodies_obj_list, zb_left.obj_param.enable_tracking, zb_left.obj_param.body_format)


###
obj=bodies_obj_list_left[0]


# forearm_left=(sl.BODY_PARTS.LEFT_ELBOW, sl.BODY_PARTS.LEFT_WRIST)

forearm_vector_left=obj.keypoint[sl.BODY_PARTS.LEFT_WRIST.value]-obj.keypoint[sl.BODY_PARTS.LEFT_ELBOW.value]
upperarm_vector_left=obj.keypoint[sl.BODY_PARTS.LEFT_ELBOW.value]-obj.keypoint[sl.BODY_PARTS.LEFT_SHOULDER.value]


vector1=forearm_vector_left
vector2=upperarm_vector_left

import numpy as np


unit_vector1 = vector1 / np.linalg.norm(vector1)
unit_vector2 = vector2 / np.linalg.norm(vector2)

dot_product = np.dot(unit_vector1, unit_vector2)

angle = np.arccos(dot_product) #angle in radian


###

cv2.imshow("ZED | 2D View", image_left_playback_ocv)
cv2.waitKey(10)