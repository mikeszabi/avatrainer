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

import sys
sys.path.append(r'../body_tracking')
import json 

import inspect
import os
import pyzed.sl as sl
import cv2
import pyzed.sl as sl
import cv_viewer.tracking_viewer as cv_viewer


BODY_18_definitions={'keypoints_to_index' : {'LEFT_HIP': sl.BODY_PARTS.LEFT_HIP.value,
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
                      'NECK':sl.BODY_PARTS.NECK.value},
                     'keypoints_relevancy' : {'LEFT_HIP': 100,
                                           'RIGHT_HIP': 100,
                                           'LEFT_KNEE': 100,
                                           'RIGHT_KNEE': 100, 
                                           'LEFT_ANKLE': 100, 
                                           'RIGHT_ANKLE': 100, 
                                           'LEFT_SHOULDER': 100,  
                                           'RIGHT_SHOULDER': 100, 
                                           'LEFT_ELBOW': 100, 
                                           'RIGHT_ELBOW': 100, 
                                           'LEFT_WRIST': 0, 
                                           'RIGHT_WRIST': 0, 
                                           'NECK':0},
                     'hierarchy' : {'spine': [],
                                  'LEFT_HIP': ['spine'], 'LEFT_KNEE': ['LEFT_HIP', 'spine'], 'LEFT_ANKLE': ['LEFT_KNEE', 'LEFT_HIP', 'spine'],
                                  'RIGHT_HIP': ['spine'], 'RIGHT_KNEE': ['RIGHT_HIP', 'spine'], 'RIGHT_ANKLE': ['RIGHT_KNEE', 'RIGHT_HIP', 'spine'],
                                  'NECK': ['spine'],
                                  'LEFT_SHOULDER': ['NECK', 'spine'], 'LEFT_ELBOW': ['LEFT_SHOULDER', 'NECK', 'spine'], 'LEFT_WRIST': ['LEFT_ELBOW', 'LEFT_SHOULDER', 'NECK', 'spine'],
                                  'RIGHT_SHOULDER': ['NECK', 'spine'], 'RIGHT_ELBOW': ['RIGHT_SHOULDER', 'NECK', 'spine'], 'RIGHT_WRIST': ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'NECK', 'spine']
                                 },
                     'connections' : [['spine', 'LEFT_HIP'], ['LEFT_HIP', 'LEFT_KNEE'], ['LEFT_KNEE', 'LEFT_ANKLE'],
                                     ['spine', 'RIGHT_HIP'], ['RIGHT_HIP', 'RIGHT_KNEE'], ['RIGHT_KNEE', 'RIGHT_ANKLE'],
                                     ['spine', 'NECK'], ['NECK', 'LEFT_SHOULDER'], ['LEFT_SHOULDER', 'LEFT_ELBOW'], ['LEFT_ELBOW', 'LEFT_WRIST'],
                                     ['NECK', 'RIGHT_SHOULDER'], ['RIGHT_SHOULDER', 'RIGHT_ELBOW'], ['RIGHT_ELBOW', 'RIGHT_WRIST']
                                   ]
                     }


def props(obj):
    # class values to dict
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr

def bodyparts_to_dict(body_model):
    # enum to dict
    if body_model=='POSE_34':
        body_parts_enum=sl.BODY_PARTS_POSE_34
    else:
        body_parts_enum=sl.BODY_PARTS_POSE_18
    keypoints_to_index={i.name: i.value for i in body_parts_enum} 
    return keypoints_to_index


    
def keypoints_to_dict(kpts,keypoints_to_index=BODY_18_definitions['keypoints_to_index']):
    # using ZED's convention
    # its easier to manipulate keypoints by joint name
    # kpts: 3x18 keypoint matrix
   
    def add_spine(kpts_dict):

        #add spine kpts
        spine = kpts_dict['RIGHT_HIP'] + (kpts_dict['LEFT_HIP'] - kpts_dict['RIGHT_HIP'])/2
        kpts_dict['spine'] = spine

        return kpts_dict

    kpts_dict = {}
    for key, k_index in keypoints_to_index.items():
        # python indexing starts from 0!
        kpts_dict[key] = kpts[:,k_index]
        
    add_spine(kpts_dict)

    kpts_dict['joints'] = list(keypoints_to_index.keys())
    kpts_dict['joints'].append('spine')
    
    kpts_dict['root_joint'] = 'spine'

    return kpts_dict

################ handle sequence json

def init_json(sequence_name,camera_info,obj_param,body_keypoint_definitions=BODY_18_definitions):
    seq_json={}
    seq_json['sequence_name']=sequence_name
    
    seq_json['camera_fps']=camera_info.camera_fps
    seq_json['camera_resolution']=[camera_info.camera_resolution.width,camera_info.camera_resolution.height]
    
    seq_json['detection_model']=obj_param.detection_model.name
    
    seq_json['body_model']=obj_param.body_format.name
    seq_json['body_keypoint_definitions']=BODY_18_definitions
    seq_json['seq_data']={}
    return seq_json
    

def get_frame_body_data(body_id,bodies,svo_position,is_inserted_frame=False):
    body_json={}
    body_json['timestamp_seconds']=bodies.timestamp.get_seconds()
    body_json['is_inserted_frame']=False
    body_json['svo_position']=svo_position

    tracked_body=None
    if len(bodies.object_list)>0:
        i=0
        while True:
            if bodies.object_list[i].id==body_id:
                tracked_body=bodies.object_list[i] # check if any
                break
            i+=1
    if tracked_body is not None:
        body_json['keypoint']=tracked_body.keypoint.tolist()
        body_json['keypoint_confidence']=tracked_body.keypoint_confidence.tolist()
    else:
        body_json['keypoint']=[]
        body_json['keypoint_confidence']=[]
    return body_json
    
    

filepath=r'../store/terdfelhuzas_right_front_2023_10_17_14_15_24.svo'
visualize_on=True

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
        print(svo_position)
        
        body_json=get_frame_body_data(body_id,bodies,svo_position)
        seq_json['seq_data'][svo_position]=body_json
        
        
        # Grab a new image
        status = zed.grab()
        
    print("SVO ends with: {0}".format(status))
       

    image.free(sl.MEM.CPU)
    # Disable modules and close camera
    zed.disable_object_detection()
    zed.disable_positional_tracking()
    zed.close()
    
    
    out_filepath=filepath.replace('svo','json')
        
    with open(out_filepath, "w") as outfile: 
        json.dump(seq_json, outfile)


if __name__ == "__main__":
    main()
   