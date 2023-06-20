#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 22:16:27 2023

@author: itqs
"""


"""
   This sample shows how to detect a human bodies and draw their 
   modelised skeleton in an OpenGL window
   #https://stackoverflow.com/questions/55919337/creating-capture-button-on-window
   #https://github.com/stereolabs/self.zed-opencv/tree/master/python
   # https://www.pythontutorial.net/python-concurrency/python-threading/

"""
import os
import threading
import cv2
import sys
import pyzed.sl as sl
import cv_viewer.tracking_viewer as cv_viewer
import numpy as np


class ZED_body:
    def __init__(self):

        # Create a Camera object
        # self.zed = sl.Camera()
        # self.zed_playback = sl.Camera()
        
        #self.image_left_recorded_ocv=None
        # self.svo_position=0
        
        self.liveOn=threading.Event()
        self.liveRec=threading.Event()
        
        self.playbackOn_right=threading.Event()
        
        self.output_path=r"../store"
        # self.isRecording=False
    
        # Create a InitParameters object and set configuration parameters
        self.init_params_live = sl.InitParameters()
        self.init_params_live.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
        self.init_params_live.coordinate_units = sl.UNIT.METER          # Set coordinate units
        #init_params_live.depth_mode = sl.DEPTH_MODE.ULTRA
        self.init_params_live.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
             
        
        self.camera_info=self.check_zed(self.init_params_live)


        # Enable Positional tracking (mandatory for object detection)
        self.positional_tracking_parameters = sl.PositionalTrackingParameters()
        # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
        self.positional_tracking_parameters.set_as_static = True
        
        self.obj_param = sl.ObjectDetectionParameters()
        self.obj_param.enable_body_fitting = True            # Smooth skeleton move
        self.obj_param.enable_tracking = True                # Track people across images flow
        self.obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST 
        self.obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use
        
        self.recordingParameters = sl.RecordingParameters()
        self.recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H264
        self.recordingParameters.video_filename = os.path.join(self.output_path,'test.svo')
    
        self.obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
        self.obj_runtime_param.detection_confidence_threshold = 40
    

        # 2D viewer utilities
        self.display_resolution = sl.Resolution(min(self.camera_info.camera_resolution.width, 960), min(self.camera_info.camera_resolution.height, 540))
        self.image_scale = [self.display_resolution.width / self.camera_info.camera_resolution.width
                     , self.display_resolution.height / self.camera_info.camera_resolution.height]


        
    def check_zed(self,init_params):
        zed = sl.Camera()
        # Open the camera
        print("Connecting ZED....")
        err = zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print("ZED is not connected")
            camera_info=None    
        else:
            print("ZED is connected")
            camera_info = zed.get_camera_information()

        zed.close()

        return camera_info
        

            
    def live(self,live_queue,svo_file):
        
        self.liveOn.set()
        zed_live = sl.Camera()
        live_image = sl.Mat()
        bodies = sl.Objects()

        self.recordingParameters.video_filename = os.path.join(self.output_path,svo_file)

        print("ZED live...")
        status = zed_live.open(self.init_params_live)
        if status != sl.ERROR_CODE.SUCCESS:
            print("ZED live is not connected")
        else:
            print("ZED live is connected")
 
        # Enable Object Detection and Positional Tracking module
        
        zed_error = zed_live.enable_positional_tracking(self.positional_tracking_parameters)
        print(self.obj_param)

        zed_error = zed_live.enable_object_detection(self.obj_param)
        print(zed_error)

        i_frame=0    
        is_Recording=False
        while self.liveOn.is_set():
            if self.liveRec.is_set():
                if not is_Recording:
                    err = zed_live.enable_recording(self.recordingParameters)
                    print(err)
                    print(f"[INFO] Recording to: {self.recordingParameters.video_filename}")
                    if err == sl.ERROR_CODE.SUCCESS:
                        print("ZED is recording")
                    else:
                        print("ZED is not recording")    
                    is_Recording=True
                    i_frame=0
            else:
                if is_Recording:
                    zed_live.disable_recording()
                    print("ZED is not recording")
                    is_Recording=False
                    i_frame=0
            if zed_live.grab() == sl.ERROR_CODE.SUCCESS:
                zed_live.retrieve_image(live_image,  sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
                zed_live.retrieve_objects(bodies, self.obj_runtime_param)
                #https://www.stereolabs.com/docs/object-detection/using-object-detection/
                # for obj in bodies.object_list:
                #     print("{} {}".format(obj.id, obj.position))
                image_left_live_ocv = live_image.get_data()
                cv_viewer.render_2D(image_left_live_ocv,self.image_scale,bodies.object_list, self.obj_param.enable_tracking, self.obj_param.body_format)
                if is_Recording:
                    i_frame+=1
                cur_frame={'image_left_live_ocv':image_left_live_ocv.copy(),
                           'bodypoints':bodies.object_list,
                           'position':i_frame}
                # check if the queue has space
                if not live_queue.full():
                	# add an item to the queue
                	live_queue.put_nowait(cur_frame)
                else:
                    print('live queue full')
            # else:
            #     print("NO live image")
            #     # zed_playback.set_svo_position(0)
            #     exit_live=True

                
        live_image.free(sl.MEM.CPU)    
        zed_live.close()   
        self.liveOn.clear()
            
        
        
    def playback(self,playback_queue,svo_file):
        
        self.playbackOn_right.set()
        
        zed_playback = sl.Camera()
        svo_image = sl.Mat()

        
        self.init_params_playback = sl.InitParameters()
        self.init_params_playback.set_from_svo_file(svo_file)
        
        print(f'ZED playback: {svo_file}')
        
        status = zed_playback.open(self.init_params_playback)
        if status != sl.ERROR_CODE.SUCCESS:
            print("ZED playback is not connected")
        else:
            print("ZED playback is connected")
        while self.playbackOn_right.is_set():
            
            status=zed_playback.grab()
            if status == sl.ERROR_CODE.SUCCESS:
                # Read side by side frames stored in the SVO
                zed_playback.retrieve_image(svo_image,  sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
                # Get frame count
                image_left_recorded_ocv = svo_image.get_data()
                svo_position = zed_playback.get_svo_position();
                print(svo_position)
            elif status == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
                print("SVO end has been reached.")#" Looping back to first frame")
                #zed_playback.set_svo_position(0)
                self.playbackOn_right.clear()
            else:
                print("SVO reading error")
                self.playbackOn_right.clear()
                
            cur_frame={'image_left_playback_ocv':image_left_recorded_ocv.copy(),'position':svo_position}
            # check if the queue has space
            if not playback_queue.full():
            	# add an item to the queue
            	playback_queue.put_nowait(cur_frame)
            else:
                print('live queue full')
        
        svo_image.free(sl.MEM.CPU)
        zed_playback.close()

    
    def __del__(self):

        # self.image.free(sl.MEM.CPU)
        # Disable modules and close camera
        self.zed.disable_object_detection()
        self.zed.disable_positional_tracking()
        self.zed.close()
        