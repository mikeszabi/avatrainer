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
"""
import cv2
import sys
import pyzed.sl as sl
import cv_viewer.tracking_viewer as cv_viewer
import numpy as np


class ZED_body:
    def __init__(self):

        # Create a Camera object
        self.zed = sl.Camera()
        
        self.output_path=r"../store/test.svo"
        self.isRecording=False
    
        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
        init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
        #init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        
        # # If applicable, use the SVO given as parameter
        # # Otherwise use self.zed live stream
        # if len(sys.argv) == 2:
        #     filepath = sys.argv[1]
        #     print("Using SVO file: {0}".format(filepath))
        #     init_params.svo_real_time_mode = True
        #     init_params.set_from_svo_file(filepath)

        # Open the camera
        print("Connecting ZED....")
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            print("ZED is not connected")
        else:
            print("ZED is connected")

        # Enable Positional tracking (mandatory for object detection)
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
        # positional_tracking_parameters.set_as_static = True
        self.zed.enable_positional_tracking(positional_tracking_parameters)
        
        self.obj_param = sl.ObjectDetectionParameters()
        self.obj_param.enable_body_fitting = True            # Smooth skeleton move
        self.obj_param.enable_tracking = True                # Track people across images flow
        self.obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_FAST 
        self.obj_param.body_format = sl.BODY_FORMAT.POSE_18  # Choose the BODY_FORMAT you wish to use
        
        self.recordingParameters = sl.RecordingParameters()
        self.recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H264
        self.recordingParameters.video_filename = self.output_path
        

        # Enable Object Detection module
        self.zed.enable_object_detection(self.obj_param)
    
        self.obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
        self.obj_runtime_param.detection_confidence_threshold = 40
    
        # Get self.zed camera information
        self.camera_info = self.zed.get_camera_information()

        # 2D viewer utilities
        self.display_resolution = sl.Resolution(min(self.camera_info.camera_resolution.width, 960), min(self.camera_info.camera_resolution.height, 540))
        self.image_scale = [self.display_resolution.width / self.camera_info.camera_resolution.width
                     , self.display_resolution.height / self.camera_info.camera_resolution.height]

        # Create OpenGL viewer
        # viewer = gl.GLViewer()
        # viewer.init(camera_info.calibration_parameters.left_cam, self.obj_param.enable_tracking,self.obj_param.body_format)
    
        # Create self.zed objects filled in the main loop
        self.bodies = sl.Objects()
        self.image = sl.Mat()
        
    def grab_image(self):
        # Grab an image
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve left image
            self.zed.retrieve_image(self.image, sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
            # Retrieve objects
            self.zed.retrieve_objects(self.bodies, self.obj_runtime_param)

      
            image_left_ocv = self.image.get_data()
            cv_viewer.render_2D(image_left_ocv,self.image_scale,self.bodies.object_list, self.obj_param.enable_tracking, self.obj_param.body_format)
            print(len(self.bodies.object_list))
            print(image_left_ocv.shape)
        else:
            image_left_ocv=None
        return image_left_ocv
    
    def record_start(self):

        if not self.isRecording:
            err = self.zed.enable_recording(self.recordingParameters)
            print(err)
            if err == sl.ERROR_CODE.SUCCESS:
                print("ZED is recording")
                self.isRecording=True
            else:
                print("ZED is not recording")
                self.isRecording=False
    
    def record_end(self):
        if self.isRecording:
            err = self.zed.disable_recording()
            if err == sl.ERROR_CODE.SUCCESS:
                print("ZED is not recording")
                self.isRecording=False

    
    def __del__(self):

        self.image.free(sl.MEM.CPU)
        # Disable modules and close camera
        self.zed.disable_object_detection()
        self.zed.disable_positional_tracking()
        self.zed.close()
        