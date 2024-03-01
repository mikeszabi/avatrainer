#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 09:07:22 2024

@author: szabi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 12:38:16 2023

@author: itqs
"""
import os
import json
import sys
sys.path.append(r'../measure')
import threading
import queue
import zed_wrapper
from body_joint_angles import BodyJoints
from cv_viewer.utils import *
import cv_viewer.tracking_viewer as cv_viewer

import cv2


def main():

    filepath_1=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.svo'
    
    
    bodyjoints_cur=BodyJoints()    
    
    step_by_step=5
    
    thread_cur=threading.Thread()
    queue_cur = queue.Queue()
    
    liveEvent_cur = threading.Event()
    recordEvent_cur = threading.Event()
    playbackEvent_cur = threading.Event()
    playbackStartEvent_cur = threading.Event()
      
    
    zb_cur=zed_wrapper.ZED_body()
    
    playbackEvent_cur.set()
    playbackStartEvent_cur.clear()
    thread_cur = threading.Thread(target=zb_cur.playback, args=((queue_cur,playbackEvent_cur,playbackStartEvent_cur,
                                                                   filepath_1,step_by_step,False)))
    
    
    thread_cur.start()  
    
        
    imdat_cur=None
    bodies_obj_list_cur=[]
    svo_pos_cur=step_by_step
    
    
    im_h = cv2.imread(r"../assets/personal_trainer.jpg", cv2.IMREAD_COLOR)
    scale_percent = 50 # percent of original size
    width = int(im_h.shape[1] * scale_percent / 100)
    height = int(im_h.shape[0] * scale_percent / 100)
    dim = (width, height)
      
    # resize image
    image_cur_playback_ocv = cv2.resize(im_h, dim, interpolation = cv2.INTER_AREA)
     
    
    key=0
    while key != 27:  # for esc
    
        
        if queue_cur.qsize()>0:
            imdat_cur=queue_cur.get()
        else:
            imdat_cur=None
      
    
        if imdat_cur is not None:
            bodies_obj_list_cur=imdat_cur['bodypoints']
            image_cur_playback_ocv=imdat_cur['image_ocv']
            svo_pos_cur=imdat_cur['position']
     
            
        if len(bodies_obj_list_cur)>0:
            
            # bodies_obj_list[0].keypoint[sl.BODY_PARTS.cur_HIP.value]
            
            ###
            obj_cur=bodies_obj_list_cur[0]
       
    
            kpts_dict_cur=bodyjoints_cur.calculate(obj_cur.keypoint)
    
            #### visualize
            cv_viewer.render_2D(image_cur_playback_ocv,zb_cur.image_scale,bodies_obj_list_cur, zb_cur.body_param.enable_tracking, zb_cur.body_param.body_format)
            
            image_cur_playback_ocv=cv2.putText(image_cur_playback_ocv, str(svo_pos_cur), (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
    
        ###
    
            bodyjoints_cur.draw_skeleton_from_joint_coordinates()
    
        
        cv2.imshow("ZED | 2D View", image_cur_playback_ocv)
        key=cv2.waitKey(0)
    
       
        if key == 97 or key==115: #a / s
            playbackStartEvent_cur.set()
            
    cv2.destroyAllWindows()   
    playbackEvent_cur.clear()

if __name__ == "__main__":
    main()