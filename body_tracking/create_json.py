#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 13:57:04 2023

@author: mikeszabi
"""
"""
[<BODY_PARTS.NOSE: 0>,
 <BODY_PARTS.NECK: 1>,
 <BODY_PARTS.RIGHT_SHOULDER: 2>,
 <BODY_PARTS.RIGHT_ELBOW: 3>,
 <BODY_PARTS.RIGHT_WRIST: 4>,
 <BODY_PARTS.LEFT_SHOULDER: 5>,
 <BODY_PARTS.LEFT_ELBOW: 6>,
 <BODY_PARTS.LEFT_WRIST: 7>,
 <BODY_PARTS.RIGHT_HIP: 8>,
 <BODY_PARTS.RIGHT_KNEE: 9>,
 <BODY_PARTS.RIGHT_ANKLE: 10>,
 <BODY_PARTS.LEFT_HIP: 11>,
 <BODY_PARTS.LEFT_KNEE: 12>,
 <BODY_PARTS.LEFT_ANKLE: 13>,
 <BODY_PARTS.RIGHT_EYE: 14>,
 <BODY_PARTS.LEFT_EYE: 15>,
 <BODY_PARTS.RIGHT_EAR: 16>,
 <BODY_PARTS.LEFT_EAR: 17>,
 <BODY_PARTS.LAST: 18>]
"""

import inspect
import os
import pyzed.sl as sl
import cv2
import pyzed.sl as sl
import cv_viewer.tracking_viewer as cv_viewer

joint_hierarchy = {'hips': [],
             'LEFT_HIP': ['hips'], 'LEFT_KNEE': ['LEFT_HIP', 'hips'], 'LEFT_ANKLE': ['LEFT_KNEE', 'LEFT_HIP', 'hips'],
             'RIGHT_HIP': ['hips'], 'RIGHT_KNEE': ['RIGHT_HIP', 'hips'], 'RIGHT_ANKLE': ['RIGHT_KNEE', 'RIGHT_HIP', 'hips'],
             'NECK': ['hips'],
             'LEFT_SHOULDER': ['NECK', 'hips'], 'LEFT_ELBOW': ['LEFT_SHOULDER', 'NECK', 'hips'], 'LEFT_WRIST': ['LEFT_ELBOW', 'LEFT_SHOULDER', 'NECK', 'hips'],
             'RIGHT_SHOULDER': ['NECK', 'hips'], 'RIGHT_ELBOW': ['RIGHT_SHOULDER', 'NECK', 'hips'], 'RIGHT_WRIST': ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'NECK', 'hips']
            }

def props(obj):
    # class values to dict
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr

def bodyparts_todict(body_model):
    # enum to dict
    if body_model=='POSE_34':
        body_parts_enum=sl.BODY_PARTS_POSE_34
    else:
        body_parts_enum=sl.BODY_PARTS_POSE_18
    keypoints_to_index={i.name: i.value for i in body_parts_enum} 
    return keypoints_to_index
    


def init_json(sequence_name,camera_info,obj_param):
    seq_json={}
    seq_json['camera_fps']=camera_info.camera_fps
    seq_json['camera_resolution']=[camera_info.camera_resolution.width,camera_info.camera_resolution.height]
    
    seq_json['detection_model']=obj_param.detection_model.name
    
    seq_json['body_model']=obj_param.body_format.name
    seq_json['keypoints_to_index']=bodyparts_todict(seq_json['body_model'])
    return seq_json
    

def add_frame_body_data(seq_json,body_id,bodies,frame_number):
    body_json={}
    body_json['timestamp_seconds']=bodies.timestamp.get_seconds()

    tracked_body=None
    if len(bodies.object_list)>0:
        i=0
        while True:
            if bodies.object_list[i].id==body_id:
                tracked_body=bodies.object_list[i] # check if any
                break
            i+=1
    if tracked_body is not None:
        body_json['keypoint']=tracked_body.keypoint
        body_json['keypoint_confidence']=tracked_body.keypoint_confidence
    else:
        body_json['keypoints']=[]
        body_json['keypoint_confidence']=[]
    
    

filepath=r'../store/kitores_oldal_2_2023_06_23_11_09_27_cut.svo'
visualize_on=False

def main():

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
    # If the camera is static, uncomment the following line to have better performances and boxes sticked to the ground.
    positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)
    
    obj_param = sl.ObjectDetectionParameters()
    obj_param.enable_body_fitting = True            # Smooth skeleton move
    obj_param.enable_tracking = True               # Track people across images flow
    obj_param.detection_model = sl.DETECTION_MODEL.HUMAN_BODY_ACCURATE
    obj_param.body_format = sl.BODY_FORMAT.POSE_18 # Choose the BODY_FORMAT you wish to use

    # Enable Object Detection module
    zed.enable_object_detection(obj_param)

    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_param.detection_confidence_threshold = 40

    # Get ZED camera information
    camera_info = zed.get_camera_information()


    # 2D viewer utilities
    display_resolution = sl.Resolution(min(camera_info.camera_resolution.width, 1280), min(camera_info.camera_resolution.height, 720))
    image_scale = [display_resolution.width / camera_info.camera_resolution.width
                 , display_resolution.height / camera_info.camera_resolution.height]

   
    # Create ZED objects filled in the main loop
    bodies = sl.Objects()
    image = sl.Mat()
    c=-1
    body_id=None
    
    seq_json=init_json(os.path.basename(filepath),camera_info,obj_param)
    
    status=zed.grab()
    while status==sl.ERROR_CODE.SUCCESS:
        
        # Retrieve left image
        zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
        # Retrieve objects
        zed.retrieve_objects(bodies, obj_runtime_param)
        if (body_id is None) and (len(bodies.object_list)>0):
            # fixing first seen body id!
            body_id=bodies.object_list[0].id

        # Update OCV view
        if visualize_on:
            image_left_ocv = image.get_data()
            cv_viewer.render_2D(image_left_ocv,image_scale,bodies.object_list, obj_param.enable_tracking, obj_param.body_format)
            cv2.imshow("ZED | 2D View", image_left_ocv)
            c=cv2.waitKey(10)
        
        svo_position = zed.get_svo_position()
        
        add_frame_body_data(seq_json,body_id,bodies,svo_position)
        
        
        # Grab a new image
        status = zed.grab()
        
    print("SVO ends with: {0}".format(status))
       

    image.free(sl.MEM.CPU)
    # Disable modules and close camera
    zed.disable_object_detection()
    zed.disable_positional_tracking()
    zed.close()
    
    


if __name__ == "__main__":
    main()
   