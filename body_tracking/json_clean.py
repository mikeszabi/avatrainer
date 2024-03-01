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
from icurve import Interactive3DCurve

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import CubicSpline, make_interp_spline, interp1d
from scipy.interpolate import splprep, splev

def save_json(out_json_filepath,seq_json,new_points):

    seq_json_new={}
    seq_json_new['sequence_name']=seq_json['sequence_name']
    seq_json_new['camera_fps']=seq_json['camera_fps']
    seq_json_new['camera_resolution']=seq_json['camera_resolution']
    seq_json_new['detection_model']=seq_json['detection_model']
    seq_json_new['body_model']=seq_json['body_model']
    seq_json_new['body_keypoint_definitions']=seq_json['body_keypoint_definitions']
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_HIP']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_HIP']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_KNEE']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_KNEE']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_ANKLE']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_ANKLE']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_SHOULDER']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_SHOULDER']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_ELBOW']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_ELBOW']=100
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['LEFT_WRIST']=0
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['RIGHT_WRIST']=0
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['NECK']=0
    seq_json_new['body_keypoint_definitions']['keypoints_relevancy']['NOSE']=0
    
    seq_json_new['seq_data']={}
    for svo_pos in range(0,n_frames):
        real_svo_pos=0
        is_inserted_frame=True
        seq_json_new['seq_data'][str(svo_pos)]={}
        while True:
            if seq_json['seq_data'][str(real_svo_pos)]['svo_position']==svo_pos:
                is_inserted_frame=False
                break
            real_svo_pos+=1
        seq_json_new['is_inserted_frame']=is_inserted_frame
        if is_inserted_frame:
            seq_json_new['seq_data'][str(svo_pos)]['svo_position']=svo_pos
            seq_json_new['seq_data'][str(svo_pos)]['timestamp_seconds']=np.nan
        else:
            seq_json_new['seq_data'][str(svo_pos)]['svo_position']=real_svo_pos
            seq_json_new['seq_data'][str(svo_pos)]['timestamp_seconds']=seq_json['seq_data'][str(real_svo_pos)]['timestamp_seconds']
        
        keypoint=[]    
        for body_joint in sorted_body_joints:
            x_new,y_new,z_new = new_points[body_joint]
            keypoint.append([x_new[svo_pos],y_new[svo_pos],z_new[svo_pos]])
        seq_json_new['seq_data'][str(svo_pos)]['keypoint']=keypoint
        seq_json_new['seq_data'][str(svo_pos)]['keypoint_confidence']=[]
    
        
    
    with open(out_json_filepath, "w") as outfile: 
        json.dump(seq_json_new, outfile)
        


def interpolate_nans(arr):
    x = np.arange(len(arr))
    valid_mask = ~np.isnan(arr)
    interp_func = interp1d(x[valid_mask], arr[valid_mask], kind='nearest', bounds_error=False, fill_value='extrapolate')
    return interp_func(x)

def circular_moving_average(data, window_size):
    """
    Odd window_size is preferred
    Compute the moving average over a 1D NumPy array, assuming circular (closed) data.
    
    Parameters:
    - data: 1D NumPy array of data points.
    - window_size: The size of the moving average window.
    
    Returns:
    - moving_avgs: 1D NumPy array of moving averages, with the same length as `data`.
    """
    half_window=int(window_size/2)
    extended_data = np.concatenate((data[-half_window:], data, data[:half_window]))
    moving_avgs=[np.mean(extended_data[i-half_window:i+half_window]) for i in range(half_window,len(extended_data)-half_window)]
    
    return moving_avgs


#json_file_path=r'../store/kitores_oldal_1_2023_06_23_11_08_58_cut.json'
json_file_path=r'../store/terdfelhuzas_left_45degree_2023_10_17_14_16_12.json'
#json_file_path=r'../store/labdadobas_1good_2023_10_03_12_17_07.json'
#json_file_path=r'../store/guggolas_1good_2023_10_03_12_17_07.json'
#json_file_path=r'../store/oldalemelés_45degree_2023_10_17_14_13_19.json'
#json_file_path=r'../store/karemeles_teljes_45degree_2023_10_17_14_19_42.json'


visualize_on=True
bodyjoints=BodyJoints()

with open(json_file_path, "r") as f: 
    seq_json = json.load(f)

seq_json_clean=seq_json.copy()


frame_ids=[int(i) for i in seq_json['seq_data'].keys()]

# frame_ids=frame_ids[:60]


n_frames=np.max(frame_ids)+1
# t = np.linspace(0, 1, n_frames)
body_joints=seq_json['body_keypoint_definitions']['keypoints_to_index'].keys()
sorted_body_joints = sorted(seq_json['body_keypoint_definitions']['keypoints_to_index'].items(), key=lambda x:x[1])
sorted_body_joints=[sbj[0] for sbj in sorted_body_joints]

smoothed_points={}
filled_points={}
orig_points={}

### get coords by joint
### find start vertical position
for body_joint in sorted_body_joints:

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
        
        
    # List of 3D points
    points = np.array(pts_j)
    # Create a parameter to interpolate along
    
    x_coords, y_coords, z_coords = points.T
    
    
    if body_joint=="RIGHT_ANKLE":
        y_start_right_ankle=np.mean(y_coords[0:5])
        # y_shift_right=y_coords-y_start_right_ankle
    if body_joint=="LEFT_ANKLE":
        y_start_left_ankle=np.mean(y_coords[0:5])
        # y_shift_left=y_coords-y_start_left_ankle


    orig_points[body_joint]=[x_coords,y_coords,z_coords]
    
y_start=np.min([y_start_right_ankle,y_start_left_ankle]) # ground level
print(y_start_right_ankle)
print(y_start_left_ankle)

 
###########################################################    
### Interpolate and fill nans
for body_joint in sorted_body_joints:   
    
    x_coords,y_coords,z_coords = orig_points[body_joint]
  
   
    # Fill NaNs in each coordinate
    x_filled = interpolate_nans(x_coords)
    y_filled = interpolate_nans(y_coords)
    z_filled = interpolate_nans(z_coords)
    
    # ensure staying above  ground
    y_filled=[max([y,y_start]) for y in y_filled]
    
    filled_points[body_joint]=[x_filled,y_filled,z_filled]

out_json_filepath=os.path.join(r'../store',os.path.splitext(os.path.basename(json_file_path))[0]+'_filled.json')
save_json(out_json_filepath,seq_json,filled_points)

#############################################################
######## manual filtering if needed

for body_joint in sorted_body_joints:  
    x_filled,y_filled,z_filled = filled_points[body_joint]
   
    # Create new figures
    fig = plt.figure()
    
    # Add a 3D subplot
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot for the points
    ax.scatter(x_filled, y_filled, z_filled)
    
    # Plot arrows
    for i in range(len(x_coords)-1):

        ax.quiver(x_filled[i], y_filled[i], z_filled[i],
                  x_filled[i+1]-x_filled[i],  y_filled[i+1]-y_filled[i],  z_filled[i+1]-z_filled[i],
                  arrow_length_ratio=0.1, color='blue')
    
        ax.text(x_filled[i], y_filled[i], z_filled[i], f'{i+1}', color='green')
    
    
    # Set labels
    ax.azim = -90
    ax.elev = 90
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(-0.75,0.75)
    ax.set_ylim(-1,1)
    ax.set_zlim(-3, -2)
    ax.set_title(body_joint)
    
    # Show the plot
    plt.show()


body_joint='NOSE'

x_filled,y_filled,z_filled = filled_points[body_joint]
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.azim = -90
ax.elev = 90
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
# ax.set_xlim(-0.75,0.75)
# ax.set_ylim(-1,1)
# ax.set_zlim(-3, -2)
ax.set_title(body_joint)
interactive_curve = Interactive3DCurve(fig, ax, x_filled, y_filled, z_filled)
plt.show()

filled_points[body_joint]=[interactive_curve.x,interactive_curve.y,interactive_curve.z]



out_json_filepath=os.path.join(r'../store',os.path.splitext(os.path.basename(json_file_path))[0]+'_fixed.json')
save_json(out_json_filepath,seq_json,filled_points)

################ B-spline smoothing
# for body_joint in sorted_body_joints:   
    
#     x_filled,y_filled,z_filled = filled_points[body_joint]
    
#     # close the curve
#     x_filled=np.append(x_filled,x_filled[0])
#     y_filled=np.append(y_filled,y_filled[0])
#     z_filled=np.append(z_filled,z_filled[0])
    
    
#     # B-spline smoothing
#     data = np.array([x_filled,y_filled,z_filled])
#     distances = np.sqrt(((data[:-1] - data[1:]) ** 2).sum(axis=0))
#     t_new = np.insert(distances.cumsum(), 0, 0)
#     t_new=t_new/t_new[-1]
    
#     tck, u= splprep(data, s=0.1, per=True, k=3)
#     data_smooth = splev(t_new, tck)
    
#     x_smooth, y_smooth, z_smooth = data_smooth
    
#     smoothed_points[body_joint]=[x_smooth,y_smooth,z_smooth]
# out_json_filepath=os.path.join(r'../store',os.path.splitext(os.path.basename(json_file_path))[0]+'_clean.json')

#########################################################
############# circular moving avarage
window_size=9
for body_joint in sorted_body_joints:   
    x_filled,y_filled,z_filled = filled_points[body_joint]

    # window_size=3
    x_smooth= circular_moving_average(x_filled, window_size)
    # window_size=3
    y_smooth= circular_moving_average(y_filled, window_size)
    # window_size=5
    z_smooth= circular_moving_average(z_filled, window_size)
    smoothed_points[body_joint]=[x_smooth,y_smooth,z_smooth]

out_json_filepath=os.path.join(r'../store',os.path.splitext(os.path.basename(json_file_path))[0]+'_smooth.json')
save_json(out_json_filepath,seq_json,smoothed_points)

##############################################################################

for body_joint in sorted_body_joints:  
    x_coords,y_coords,z_coords = orig_points[body_joint] 
    x_smooth,y_smooth,z_smooth = smoothed_points[body_joint]    
    
    # Create new figures
    fig = plt.figure()
    
    # Add a 3D subplot
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot for the points
    ax.scatter(x_coords, y_coords, z_coords)
    
    # Plot arrows
    for i in range(len(x_coords)-1):

        ax.quiver(x_coords[i], y_coords[i], z_coords[i],
                  x_coords[i+1]-x_coords[i],  y_coords[i+1]-y_coords[i],  z_coords[i+1]-z_coords[i],
                  arrow_length_ratio=0.1, color='blue')
    
        ax.text(x_coords[i], y_coords[i], z_coords[i], f'{i+1}', color='green')
    ax.plot(x_smooth, y_smooth, z_smooth, color='red', label='Smoothed Path')
    
    
    # Set labels
    ax.azim = -90
    ax.elev = 90
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(-0.75,0.75)
    ax.set_ylim(-1,1)
    ax.set_zlim(-3, -2)
    ax.set_title(body_joint)
    
    # Show the plot
    plt.show()


############################################    

