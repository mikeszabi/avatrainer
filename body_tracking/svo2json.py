#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:33:29 2023

@author: itqs
"""

import sys
sys.path.append(r'../measure')
import json 
import os
import pyzed.sl as sl
import cv2
import cv_viewer.tracking_viewer as cv_viewer

import body_keypoints
#import joint_angles
from body_joint_angles import BodyJoints


filepath=r'../store/terpeszzar_front_2023_10_17_14_17_41.svo'
visualize_on=True

def main():

    bodyjoints=BodyJoints()    

    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
    init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    
    

    # filepath = sys.argv[1]
    print("Using SVO file: {0}".format(filepath))
    init_params.svo_real_time_mode = False
    init_params.set_from_svo_file(filepath)

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    # If the camera is static, uncomment the following line to have better performances
    positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)
    
    body_param = sl.BodyTrackingParameters()
    body_param.enable_tracking = True                # Track people across images flow
    body_param.enable_body_fitting = False            # Smooth skeleton move
    body_param.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST 
    body_param.body_format = sl.BODY_FORMAT.BODY_18  # Choose the BODY_FORMAT you wish to use

    # Enable Object Detection module
    zed.enable_body_tracking(body_param)

    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 40

    # Get ZED camera information
    camera_info = zed.get_camera_information()
    # 2D viewer utilities
    display_resolution = sl.Resolution(min(camera_info.camera_configuration.resolution.width, 1280), min(camera_info.camera_configuration.resolution.height, 720))
    image_scale = [display_resolution.width / camera_info.camera_configuration.resolution.width
                 , display_resolution.height / camera_info.camera_configuration.resolution.height]


   
    # Create ZED objects filled in the main loop
    bodies = sl.Bodies()
    image = sl.Mat()
    c=-1
    body_id=None
    
    seq_json=body_keypoints.init_json(os.path.basename(filepath),camera_info,body_param)
    
    status=zed.grab()
    while status==sl.ERROR_CODE.SUCCESS:
        
        # Retrieve left image
        zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
        # Retrieve objects
        zed.retrieve_bodies(bodies, body_runtime_param)
        if (body_id is None) and (len(bodies.body_list)>0):
            # fixing first seen body id!
            body_id=bodies.body_list[0].id

        # Update OCV view
        if visualize_on:
            image_left_ocv = image.get_data()
            cv_viewer.render_2D(image_left_ocv,image_scale,bodies.body_list, body_param.enable_tracking, body_param.body_format)
            cv2.imshow("ZED | 2D View", image_left_ocv)
            c=cv2.waitKey(10)
        
        svo_position = zed.get_svo_position()
        print(svo_position)
        
        body_json=body_keypoints.get_frame_body_data(body_id,bodies,svo_position)
        seq_json['seq_data'][svo_position]=body_json
        
        
        # Grab a new image
        status = zed.grab()
        
        obj=bodies.body_list[0]
        # kpts_left=joint_angles.calculate(obj)
        kpts_dict=bodyjoints.calculate(obj)
        bodyjoints.draw_skeleton_from_joint_coordinates()
        
    print("SVO ends with: {0}".format(status))
       
    if visualize_on:
        cv2.destroyAllWindows()

    # Disable modules and close camera
    zed.disable_object_detection()
    zed.disable_positional_tracking()
    zed.close()
    
    
    out_filepath=filepath.replace('svo','json')
        
    with open(out_filepath, "w") as outfile: 
        json.dump(seq_json, outfile)


if __name__ == "__main__":
    main()
   