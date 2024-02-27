#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 17:48:11 2024

@author: szabi
"""
import sys
sys.path.append(r'../measure')
import json 
import os
import numpy as np


import body_keypoints
#import joint_angles
from body_joint_angles import BodyJoints

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import CubicSpline, make_interp_spline, interp1d
from scipy.interpolate import splprep, splev


def interpolate_nans(arr):
    x = np.arange(len(arr))
    valid_mask = ~np.isnan(arr)
    interp_func = interp1d(x[valid_mask], arr[valid_mask], kind='nearest', bounds_error=False, fill_value='extrapolate')
    return interp_func(x)



filepath=r'../store/kitores_oldal_1_2023_06_23_11_08_58_cut.svo'
#filepath=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.svo'
#filepath=r'../store/labdadobas_1good_2023_10_03_12_17_07.svo'
#filepath=r'../store/guggolas_1good_2023_10_03_12_17_07.svo'
#filepath=r'../store/oldalemelés_45degree_2023_10_17_14_13_19.svo'
#filepath=r'../store/karemeles_teljes_45degree_2023_10_17_14_19_42.svo'


visualize_on=True
bodyjoints=BodyJoints()

json_file_path=filepath.replace('svo','json')
with open(json_file_path, "r") as f: 
    seq_json = json.load(f)

seq_json_clean=seq_json.copy()


frame_ids=[int(i) for i in seq_json['seq_data'].keys()]
n_frames=np.max(frame_ids)+1
body_joints=seq_json['body_keypoint_definitions']['keypoints_to_index'].keys()


smoothed_points={}

for body_joint in body_joints:

    # body_joint='LEFT_KNEE'
    j_id=seq_json['body_keypoint_definitions']['keypoints_to_index'][body_joint]
    pts_j=[]
    
    for i in range(0,n_frames):
        
        if i in frame_ids:
    
            body_json=seq_json['seq_data'][str(i)]
            body_kpts=np.asarray(body_json['keypoint'])
            
            pt_j=body_kpts[j_id,:]
            pts_j.append(pt_j)
        
        else:
            print('missing_frame')
            pts_j.append([np.nan,np.nan,np.nan])
        
        #body_kpts=obj.keypoint
        # kpts_dict=bodyjoints.calculate(body_kpts) #np.asarray(body_json['keypoint']) == obj.keypoint
        # bodyjoints.draw_skeleton_from_joint_coordinates()
    
    ###############################################################################xxx
    
    
    
    # List of 3D points
    points = np.array(pts_j)
    # Create a parameter to interpolate along
    t = np.linspace(0, 1, n_frames)
    
    x_coords, y_coords, z_coords = points.T
    
    # Fill NaNs in each coordinate
    x_filled = interpolate_nans(x_coords)
    y_filled = interpolate_nans(y_coords)
    z_filled = interpolate_nans(z_coords)
    
    x_filled=np.append(x_filled,x_filled[0])
    y_filled=np.append(y_filled,y_filled[0])
    z_filled=np.append(z_filled,z_filled[0])
   
    
    # # Smoothing factor (s): Larger values mean more smoothing.
    # t = np.zeros(x_filled.shape)
    # t[1:] = np.sqrt((x_filled[1:] - x_filled[:-1])**2 + (y_filled[1:] - y_filled[:-1])**2 + (z_filled[1:] - z_filled[:-1])**2)
    # t = np.cumsum(t)
    # t /= t[-1]
    t = np.linspace(0, 1, n_frames)
    
    # # cs_x = CubicSpline(t, x_filled, bc_type='periodic')
    # # cs_y = CubicSpline(t, y_filled, bc_type='periodic')
    # # cs_z = CubicSpline(t, z_filled, bc_type='periodic')
    
    # degree = 2  # Quadratic spline
    # q_x = make_interp_spline(t, x_filled, k=degree)
    # q_y = make_interp_spline(t, y_filled, k=degree)
    # q_z = make_interp_spline(t, z_filled, k=degree)
    
    # # Generate new smoothed points
    # t_fine = np.linspace(0, 1, n_frames)
    # x_smooth = q_x(t_fine)
    # y_smooth = q_y(t_fine)
    # z_smooth = q_z(t_fine)
    
    data = np.array([x_filled,y_filled,z_filled])
    tck, u= splprep(data, s=0.05, per=True, k=3)
    data_smooth = splev(t, tck)
    
    x_smooth, y_smooth, z_smooth = data_smooth
    
    # Create a new figure
    fig = plt.figure()
    
    # Add a 3D subplot
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot for the points
    ax.scatter(x_coords, y_coords, z_coords)
    
    # Plot arrows
    for i in range(len(points)-1):
        start_point = points[i]
        end_point = points[i+1]
        ax.quiver(start_point[0], start_point[1], start_point[2],
                  end_point[0]-start_point[0], end_point[1]-start_point[1], end_point[2]-start_point[2],
                  arrow_length_ratio=0.1, color='blue')
    
        ax.text(start_point[0], start_point[1], start_point[2], f'{i+1}', color='green')
    ax.plot(x_smooth, y_smooth, z_smooth, color='red', label='Smoothed Path')
    
    
    # Set labels
    ax.azim = -90
    ax.elev = 90
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(-0.5,0.5)
    ax.set_ylim(-1,1)
    ax.set_zlim(-3, -2)
    ax.set_title(body_joint)
    
    # Show the plot
    plt.show()
    
    if body_joint=="RIGHT_ANKLE":
        y_start_right_ankle=np.mean(y_smooth[0:5])
    if body_joint=="LEFT_ANKLE":
        y_start_left_ankle=np.mean(y_smooth[0:5])


    smoothed_points[body_joint]=[x_smooth,y_smooth,z_smooth]
    
# for body_joint in body_joints:
#     x_smooth,y_smooth,z_smooth = smoothed_points[body_joint]
    
    