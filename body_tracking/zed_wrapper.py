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
import sys
import os
# import threading
# import cv2
# import sys
import pyzed.sl as sl
import cv_viewer.tracking_viewer as cv_viewer
import numpy as np


class ZED_body:
    def __init__(self):

    
        self.output_path=r"../store"
        # self.isRecording=False
    
        # Create a InitParameters object and set configuration parameters
        self.init_params_live = sl.InitParameters()
        self.init_params_live.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
        self.init_params_live.coordinate_units = sl.UNIT.METER          # Set coordinate units
        #init_params_live.depth_mode = sl.DEPTH_MODE.ULTRA
        self.init_params_live.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        self.init_params_live.camera_fps=15
             
        
        self.camera_info=self.check_zed(self.init_params_live)
        
        if self.camera_info is None:
            print('exiting')
            sys.exit()


        # Enable Positional tracking (mandatory for object detection)
        self.positional_tracking_parameters = sl.PositionalTrackingParameters()
        # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
        self.positional_tracking_parameters.set_as_static = True
        
        self.body_param = sl.BodyTrackingParameters()
        self.body_param.enable_body_fitting = True            # Smooth skeleton move
        self.body_param.enable_tracking = False                # Track people across images flow
        self.body_param.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE
        self.body_param.body_format = sl.BODY_FORMAT.BODY_18  # Choose the BODY_FORMAT you wish to use
        
        self.recordingParameters = sl.RecordingParameters()
        self.recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H264
        self.recordingParameters.video_filename = os.path.join(self.output_path,'test.svo')
    
        self.body_runtime_param = sl.BodyTrackingRuntimeParameters()
        self.body_runtime_param.detection_confidence_threshold = 40
    

        # 2D viewer utilities
        self.display_resolution = sl.Resolution(min(self.camera_info.camera_configuration.resolution.width, 960), min(self.camera_info.camera_configuration.resolution.height, 540))
        self.image_scale = [self.display_resolution.width / self.camera_info.camera_configuration.resolution.width
                     , self.display_resolution.height / self.camera_info.camera_configuration.resolution.height]


    def print_camera_information(self,camera_info):
        print("Resolution: {0}, {1}.".format(round(camera_info.camera_configuration.resolution.width, 2), camera_info.camera_configuration.resolution.height))
        print("Camera FPS: {0}.".format(camera_info.camera_configuration.fps))
        print("Firmware: {0}.".format(camera_info.camera_configuration.firmware_version))
        print("Serial number: {0}.\n".format(camera_info.serial_number))
        
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
            self.print_camera_information(camera_info)


        zed.close()

        return camera_info
        

            
    def live(self,live_queue,liveEvent,recordEvent,svo_file):
        
        zed_live = sl.Camera()
        live_image = sl.Mat()
        bodies = sl.Bodies()

        self.recordingParameters.video_filename = os.path.join(self.output_path,svo_file)

        print("ZED live...")
        status = zed_live.open(self.init_params_live)
        if status != sl.ERROR_CODE.SUCCESS:
            print("ZED live is not connected")
        else:
            print("ZED live is connected")
            self.print_camera_information(zed_live.get_camera_information())
        # self.init_params_live.save('c')
 
        # Enable Object Detection and Positional Tracking module
        
        zed_error = zed_live.enable_positional_tracking(self.positional_tracking_parameters)
        print(self.body_param)

        zed_error = zed_live.enable_body_tracking(self.body_param)
        print(zed_error)

        svo_position=0    
        is_Recording=False
        
        while liveEvent.is_set():
            
            # recording only in live mode
            if recordEvent.is_set():
                if not is_Recording:
                    err = zed_live.enable_recording(self.recordingParameters)
                    print(err)
                    print(f"[INFO] Recording to: {self.recordingParameters.video_filename}")
                    if err == sl.ERROR_CODE.SUCCESS:
                        print("ZED is recording")
                    else:
                        print("ZED is not recording")    
                    is_Recording=True
                    svo_position=0
            else:
                if is_Recording:
                    zed_live.disable_recording()
                    print("ZED is not recording")
                    is_Recording=False
                    svo_position=0
            #print(f"fps: {zed_live.get_current_fps()}")
            
            if zed_live.grab() == sl.ERROR_CODE.SUCCESS:
                zed_live.retrieve_image(live_image,  sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
                zed_live.retrieve_bodies(bodies, self.body_runtime_param)
                #https://www.stereolabs.com/docs/object-detection/using-object-detection/
                # for obj in bodies.object_list:
                #     print("{} {}".format(obj.id, obj.position))
                image_left_live_ocv = live_image.get_data()
                cv_viewer.render_2D(image_left_live_ocv,self.image_scale,bodies.body_list, self.body_param.enable_tracking, self.body_param.body_format)
                
                if is_Recording:
                    svo_position+=1
                    
                cur_frame={'image_ocv':image_left_live_ocv.copy(),
                           'bodypoints':bodies.body_list.copy(),
                           'position':svo_position}
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
        # zed_live.close()   
            
        
        
    def playback(self,playback_queue,loopEvent,playbackStartEvent,svo_file,step_by_step,real_time_mode):
        
        zed_playback = sl.Camera()
        svo_image = sl.Mat()
        bodies = sl.Bodies()


        is_firstFRAME=True
        
        # input_type = sl.InputType()
        # input_type.set_from_svo_file(svo_file)
        # init_params_playback = sl.InitParameters(input_t=input_type, svo_real_time_mode=True)
        # # init_params_playback = sl.InitParameters()
        # # init_params_playback.set_from_svo_file(svo_file)
        # init_params_playback.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
        # init_params_playback.coordinate_units = sl.UNIT.METER          # Set coordinate units
        # init_params_live.depth_mode = sl.DEPTH_MODE.ULTRA
        # init_params_playback.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        # init_params_playback.camera_fps=15
        # # init_params_playback.save('a')
        init_params_playback=self.init_params_live
        init_params_playback.svo_real_time_mode = real_time_mode
        init_params_playback.set_from_svo_file(svo_file)

        status = zed_playback.open(init_params_playback)
        if status != sl.ERROR_CODE.SUCCESS:
            print("ZED playback is not connected")
        else:
            print("ZED playback is connected")
            self.print_camera_information(zed_playback.get_camera_information())


        print(f'ZED playback: {svo_file}')
        
        # Enable Object Detection and Positional Tracking module
        
        zed_error = zed_playback.enable_positional_tracking(self.positional_tracking_parameters)

        print(self.body_param)

        zed_error = zed_playback.enable_body_tracking(self.body_param)

        print(zed_error)
        
        if step_by_step is not None:
            print(f"position set to: {step_by_step}")
            zed_playback.set_svo_position(step_by_step)
        
        
        while loopEvent.is_set():
            
            if playbackStartEvent.is_set() or is_firstFRAME:
            
                status=zed_playback.grab()
                if status == sl.ERROR_CODE.SUCCESS:
                    # Read side by side frames stored in the SVO
                    zed_playback.retrieve_image(svo_image,  sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
                    
                    zed_playback.retrieve_bodies(bodies, self.body_runtime_param)
                    #https://www.stereolabs.com/docs/object-detection/using-object-detection/
                    # for obj in bodies.body_list:
                    #     print("{} {}".format(obj.id, obj.position))
                    image_left_playback_ocv = svo_image.get_data()
                    cv_viewer.render_2D(image_left_playback_ocv,self.image_scale,bodies.body_list, self.body_param.enable_tracking, self.body_param.body_format)
                    
                    svo_position = zed_playback.get_svo_position();
                    print(f"POS: {svo_position}")
                    cur_frame={'image_ocv':image_left_playback_ocv.copy(),
                               'bodypoints':bodies.body_list.copy(),
                               'position':svo_position}
                    # check if the queue has space
                    if not playback_queue.full():
                    	# add an item to the queue
                    	playback_queue.put_nowait(cur_frame)
                    else:
                        print('live queue full')
                    
                    if step_by_step is not None: 
                        playbackStartEvent.clear()
                       
                   
                    # print(svo_position)
                elif status == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
                    print("SVO end has been reached.")#" Looping back to first frame")
                    zed_playback.set_svo_position(0)
                    #is_running=False
                else:
                    print("SVO reading error")
            
            if is_firstFRAME:
                if step_by_step is None:                    
                    zed_playback.set_svo_position(0)
                    is_firstFRAME=False   
                else:
                    zed_playback.set_svo_position(step_by_step)
                    is_firstFRAME=False   
                    
            if step_by_step is not None:  
                playbackStartEvent.wait(5)
                
                
        svo_image.free(sl.MEM.CPU)
        zed_playback.close()

    
    def __del__(self):

        # self.image.free(sl.MEM.CPU)
        # Disable modules and close camera
        self.zed.disable_body_tracking()
        self.zed.disable_positional_tracking()
        self.zed.close()
        