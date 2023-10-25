#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:38:16 2023

@author: itqs
"""
import json
import sys
sys.path.append(r'../measure')
import threading
import queue
import zed_wrapper
from oks import oks_score_bodypoints
from body_joint_angles import BodyJoints
from cv_viewer.utils import *
import cv_viewer.tracking_viewer as cv_viewer

# import pyzed.sl as sl
import cv2
import numpy as np

joint_treshold=0.99

keypoints_to_index = {'LEFT_HIP': sl.BODY_PARTS.LEFT_HIP.value,
                      'RIGHT_HIP': sl.BODY_PARTS.RIGHT_HIP.value,
                      'LEFT_KNEE': sl.BODY_PARTS.LEFT_KNEE.value,
                      'RIGHT_KNEE': sl.BODY_PARTS.RIGHT_KNEE.value, 
                      'LEFT_ANKLE': sl.BODY_PARTS.LEFT_ANKLE.value, 
                      'RIGHT_ANKLE': sl.BODY_PARTS.RIGHT_ANKLE.value, 
                      'LEFT_SHOULDER': sl.BODY_PARTS.LEFT_SHOULDER.value,  
                      'RIGHT_SHOULDER': sl.BODY_PARTS.RIGHT_SHOULDER.value, 
                      'LEFT_ELBOW': sl.BODY_PARTS.LEFT_ELBOW.value, 
                      'RIGHT_ELBOW': sl.BODY_PARTS.RIGHT_ELBOW.value, 
                      'LEFT_WRIST': sl.BODY_PARTS.LEFT_WRIST.value, 
                      'RIGHT_WRIST': sl.BODY_PARTS.RIGHT_WRIST.value, 
                      'NECK':sl.BODY_PARTS.NECK.value}

filepath_1=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.svo'
filepath_2=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.svo'

# filepath_2=r'../store/terdfelhuzas_right_45degree_2023_10_17_14_16_40.svo'
# filepath_1=r'../store_orig/labdadobas_1good_2023_10_03_12_17_07.svo'
# filepath_2=r'../store_orig/labdadobas_2bad_2023_10_03_12_17_07.svo'

bodyjoints_left=BodyJoints()    
bodyjoints_right=BodyJoints()    


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
        
        ###
        obj_left=bodies_obj_list_left[0]
        obj_right=bodies_obj_list_right[0]
   
        visibility=np.isnan(np.sum(obj_left.keypoint,axis=1))*np.isnan(np.sum(obj_right.keypoint,axis=1))==0
        
        # obj_key_score=oks_score_bodypoints(obj_left, obj_right, visibility)
        
        kpts_dict_left=bodyjoints_left.calculate(obj_left)
        kpts_dict_right=bodyjoints_right.calculate(obj_right)

        angle_diff_score=bodyjoints_left.compare_score_bodypoints(obj_left, obj_right, visibility)
    

        #### visualize
        cv_viewer.render_2D(image_left_playback_ocv,zb_left.image_scale,bodies_obj_list_left, zb_left.obj_param.enable_tracking, zb_left.obj_param.body_format)
        cv_viewer.render_2D(image_right_playback_ocv,zb_right.image_scale,bodies_obj_list_right, zb_right.obj_param.enable_tracking, zb_right.obj_param.body_format)
        
        image_left_playback_ocv=cv2.putText(image_left_playback_ocv, str(svo_pos_left), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
        image_right_playback_ocv=cv2.putText(image_right_playback_ocv, str(svo_pos_right), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)

        im_h = cv2.hconcat([image_left_playback_ocv, image_right_playback_ocv])


        i=0
        for k in keypoints_to_index.keys():
            if k in angle_diff_score.keys():
                if angle_diff_score[k]>joint_treshold:
                    color=(0,255,0)
                else:
                    color=(0,0,255)
                if not np.isnan(angle_diff_score[k]):
                    im_h = cv2.putText(im_h, k + ": " + np.array2string(angle_diff_score[k],precision=2), (850,60+i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
                    im_h = cv2.putText(im_h, k + ": " + np.array2string((180*kpts_dict_left[k+'_angles']/np.pi).astype(int)), (100,60+i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
                    im_h = cv2.putText(im_h, k + ": " + np.array2string((180*kpts_dict_right[k+'_angles']/np.pi).astype(int)), (1680,60+i), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
           
                    ind=keypoints_to_index[k]
                    center=(int(obj_right.keypoint_2d[ind][0]*zb_right.image_scale[0]+im_h.shape[1]/2),int(obj_right.keypoint_2d[ind][1]*zb_right.image_scale[1]))
                    im_h=cv2.circle(im_h, center, 3, color, 2)
            i+=25
                     
       

        # if obj_key_score>0.9925:
        #     color=(0,255,0)
        # else:
        #     color=(0,0,255)
        #im_h = cv2.putText(im_h, "{0:.3f}".format(obj_key_score), (100,30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

        # im_h=cv2.cvtColor(im_h, cv2.COLOR_BGR2RGB)
        
    ###

        bodyjoints_left.draw_skeleton_from_joint_coordinates()
        bodyjoints_right.draw_skeleton_from_joint_coordinates()        
      
    if key == 97 or key==115: #a / s
        playbackStartEvent_left.set()
    if key == 100 or key==115: #d / s
        playbackStartEvent_right.set()    

    
    cv2.imshow("ZED | 2D View", im_h)
    key=cv2.waitKey(0)

        
    
# playbackEvent_left.clear()
# playbackEvent_right.clear()