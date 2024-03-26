#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 17:48:11 2024

@author: szabi
"""
import os
import sys
sys.path.append(r'../measure')
import json 
import numpy as np


#import joint_angles
from body_joint_angles import BodyJoints

dir_path = r'../store/20240325'

fixed_json_file_path=os.path.join(dir_path,'complex1_HD1080_SN30195290_12-40-11_smooth.json')



bodyjoints=BodyJoints()

with open(fixed_json_file_path, "r") as f: 
    seq_json = json.load(f)


frame_ids=[int(i) for i in seq_json['seq_data'].keys()]
n_frames=np.max(frame_ids)+1


for i in range(0,n_frames):
    
    if i in frame_ids:

        body_json=seq_json['seq_data'][str(i)]
        body_kpts=np.asarray(body_json['keypoint'])
        
        kpts_dict=bodyjoints.calculate(body_kpts)
        bodyjoints.draw_skeleton_from_joint_coordinates()
    else:
        print('missing_frame')
    