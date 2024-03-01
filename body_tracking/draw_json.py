#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 17:48:11 2024

@author: szabi
"""
import sys
sys.path.append(r'../measure')
import json 
import numpy as np


#import joint_angles
from body_joint_angles import BodyJoints

#x fixed_json_file_path=r'../store/kitores_oldal_1_2023_06_23_11_08_58_cut_smooth.json'
fixed_json_file_path=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12_smooth.json'
#fixed_json_file_path=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.json'
#fixed_json_file_path=r'../store/labdadobas_1good_2023_10_03_12_17_07.json'
#fixed_json_file_path=r'../store/guggolas_1good_2023_10_03_12_17_07.json'
#fixed_json_file_path=r'../store/oldalemelés_45degree_2023_10_17_14_13_19.json'
#fixed_json_file_path=r'../store/karemeles_teljes_45degree_2023_10_17_14_19_42.json'

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
    