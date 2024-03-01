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
import pyzed.sl as sl


BODY_18_definitions={'keypoints_to_index' : {'NOSE': sl.BODY_18_PARTS.NOSE.value,
                      'LEFT_HIP': sl.BODY_18_PARTS.LEFT_HIP.value,
                      'RIGHT_HIP': sl.BODY_18_PARTS.RIGHT_HIP.value,
                      'LEFT_KNEE': sl.BODY_18_PARTS.LEFT_KNEE.value,
                      'RIGHT_KNEE': sl.BODY_18_PARTS.RIGHT_KNEE.value, 
                      'LEFT_ANKLE': sl.BODY_18_PARTS.LEFT_ANKLE.value, 
                      'RIGHT_ANKLE': sl.BODY_18_PARTS.RIGHT_ANKLE.value, 
                      'LEFT_SHOULDER': sl.BODY_18_PARTS.LEFT_SHOULDER.value,  
                      'RIGHT_SHOULDER': sl.BODY_18_PARTS.RIGHT_SHOULDER.value, 
                      'LEFT_ELBOW': sl.BODY_18_PARTS.LEFT_ELBOW.value, 
                      'RIGHT_ELBOW': sl.BODY_18_PARTS.RIGHT_ELBOW.value, 
                      'LEFT_WRIST': sl.BODY_18_PARTS.LEFT_WRIST.value, 
                      'RIGHT_WRIST': sl.BODY_18_PARTS.RIGHT_WRIST.value, 
                      'NECK':sl.BODY_18_PARTS.NECK.value},
                     'keypoints_relevancy' : {'NOSE': 0,
                                           'LEFT_HIP': 100,
                                           'RIGHT_HIP': 100,
                                           'LEFT_KNEE': 100,
                                           'RIGHT_KNEE': 100, 
                                           'LEFT_ANKLE': 100, 
                                           'RIGHT_ANKLE': 100, 
                                           'LEFT_SHOULDER': 100,  
                                           'RIGHT_SHOULDER': 100, 
                                           'LEFT_ELBOW': 100, 
                                           'RIGHT_ELBOW': 100, 
                                           'LEFT_WRIST': 100, 
                                           'RIGHT_WRIST': 100, 
                                           'NECK':100},
                     'hierarchy' : {'spine': [],'NOSE': ['NECK', 'spine'],
                                  'LEFT_HIP': ['spine'], 'LEFT_KNEE': ['LEFT_HIP', 'spine'], 'LEFT_ANKLE': ['LEFT_KNEE', 'LEFT_HIP', 'spine'],
                                  'RIGHT_HIP': ['spine'], 'RIGHT_KNEE': ['RIGHT_HIP', 'spine'], 'RIGHT_ANKLE': ['RIGHT_KNEE', 'RIGHT_HIP', 'spine'],
                                  'NECK': ['spine'],
                                  'LEFT_SHOULDER': ['NECK', 'spine'], 'LEFT_ELBOW': ['LEFT_SHOULDER', 'NECK', 'spine'], 'LEFT_WRIST': ['LEFT_ELBOW', 'LEFT_SHOULDER', 'NECK', 'spine'],
                                  'RIGHT_SHOULDER': ['NECK', 'spine'], 'RIGHT_ELBOW': ['RIGHT_SHOULDER', 'NECK', 'spine'], 'RIGHT_WRIST': ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'NECK', 'spine']
                                 },
                     'connections' : [['NOSE','NECK'],['spine', 'LEFT_HIP'], ['LEFT_HIP', 'LEFT_KNEE'], ['LEFT_KNEE', 'LEFT_ANKLE'],
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
    kpts_dict['joints']=[]
    for key, k_index in keypoints_to_index.items():
        if key not in ['NOSE']:
            if k_index<kpts.shape[1]:
                kpts_dict[key] = kpts[:,k_index]
                kpts_dict['joints'].append(key)
        
    add_spine(kpts_dict)
    kpts_dict['joints'].append('spine')
    
    kpts_dict['root_joint'] = 'spine'

    return kpts_dict

################ handle sequence json

def init_json(sequence_name,camera_info,body_param,body_keypoint_definitions=BODY_18_definitions):
    seq_json={}
    seq_json['sequence_name']=sequence_name
    
    seq_json['camera_fps']=camera_info.camera_configuration.fps
    seq_json['camera_resolution']=[camera_info.camera_configuration.resolution.width,camera_info.camera_configuration.resolution.height]
    
    seq_json['detection_model']=body_param.detection_model.name
    
    seq_json['body_model']=body_param.body_format.name
    seq_json['body_keypoint_definitions']=BODY_18_definitions
    seq_json['seq_data']={}
    return seq_json
    

def get_frame_body_data(body_id,bodies,svo_position,is_inserted_frame=False):
    body_json={}
    body_json['timestamp_seconds']=bodies.timestamp.get_seconds()
    body_json['is_inserted_frame']=False
    body_json['svo_position']=svo_position

    tracked_body=None
    if len(bodies.body_list)>0:
        i=0
        while True:
            if bodies.body_list[i].id==body_id:
                tracked_body=bodies.body_list[i] # check if any
                break
            i+=1
    if tracked_body is not None:
        body_json['keypoint']=tracked_body.keypoint.tolist()
        body_json['keypoint_confidence']=tracked_body.keypoint_confidence.tolist()
    else:
        body_json['keypoint']=[]
        body_json['keypoint_confidence']=[]
    return body_json
    
    
