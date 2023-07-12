#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:41:52 2023

@author: itqs
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

import pyzed.sl as sl

import numpy as np
import sys
import utils
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# def read_keypoints(filename):

#     num_keypoints = 12
#     fin = open(filename, 'r')

#     kpts = []
#     while(True):
#         line = fin.readline()
#         if line == '': break

#         line = line.split()
#         line = [float(s) for s in line]

#         line = np.reshape(line, (num_keypoints, -1))
#         kpts.append(line)

#     kpts = np.array(kpts)
#     return kpts

def obj2kpts(obj):
    kpts=np.empty([3,13])
    kpts[:,0]=obj.keypoint[5]
    kpts[:,1]=obj.keypoint[2]
    kpts[:,2]=obj.keypoint[6]
    kpts[:,3]=obj.keypoint[3]
    kpts[:,4]=obj.keypoint[7]
    kpts[:,5]=obj.keypoint[4]
    kpts[:,6]=obj.keypoint[11]
    kpts[:,7]=obj.keypoint[8]
    kpts[:,8]=obj.keypoint[12]
    kpts[:,9]=obj.keypoint[9]
    kpts[:,10]=obj.keypoint[13]
    kpts[:,11]=obj.keypoint[10]
    kpts[:,12]=obj.keypoint[1]
    return kpts

def convert_to_dictionary(kpts):
    #its easier to manipulate keypoints by joint name
    keypoints_to_index = {'lefthip': 6, 'leftknee': 8, 'leftfoot': 10,
                          'righthip': 7, 'rightknee': 9, 'rightfoot': 11,
                          'leftshoulder': 0, 'leftelbow': 2, 'leftwrist': 4,
                          'rightshoulder': 1, 'rightelbow': 3, 'rightwrist': 5,
                          'neck':12}

    kpts_dict = {}
    for key, k_index in keypoints_to_index.items():
        kpts_dict[key] = kpts[:,k_index]

    kpts_dict['joints'] = list(keypoints_to_index.keys())

    return kpts_dict


def add_hips_and_neck(kpts_dict):
    #we add two new keypoints which are the mid point between the hips and mid point between the shoulders

    #add hips kpts
    difference = kpts_dict['lefthip'] - kpts_dict['righthip']
    difference = difference/2
    hips = kpts_dict['righthip'] + difference
    kpts_dict['hips'] = hips
    kpts_dict['joints'].append('hips')


    # #add neck kpts
    # difference = kpts['leftshoulder'] - kpts['rightshoulder']
    # difference = difference/2
    # neck = kpts['rightshoulder'] + difference
    # kpts['neck'] = neck
    # kpts['joints'].append('neck')

    #define the hierarchy of the joints
    hierarchy = {'hips': [],
                 'lefthip': ['hips'], 'leftknee': ['lefthip', 'hips'], 'leftfoot': ['leftknee', 'lefthip', 'hips'],
                 'righthip': ['hips'], 'rightknee': ['righthip', 'hips'], 'rightfoot': ['rightknee', 'righthip', 'hips'],
                 'neck': ['hips'],
                 'leftshoulder': ['neck', 'hips'], 'leftelbow': ['leftshoulder', 'neck', 'hips'], 'leftwrist': ['leftelbow', 'leftshoulder', 'neck', 'hips'],
                 'rightshoulder': ['neck', 'hips'], 'rightelbow': ['rightshoulder', 'neck', 'hips'], 'rightwrist': ['rightelbow', 'rightshoulder', 'neck', 'hips']
                }

    kpts_dict['hierarchy'] = hierarchy
    kpts_dict['root_joint'] = 'hips'

    return kpts_dict

#remove jittery keypoints by applying a median filter along each axis
# def median_filter(kpts_dict, window_size = 3):

#     import copy
#     filtered = copy.deepcopy(kpts_dict)

#     from scipy.signal import medfilt


#     #apply median filter to get rid of poor keypoints estimations
#     for joint in filtered['joints']:
#         joint_kpts = filtered[joint]
#         xs = joint_kpts[:,0]
#         ys = joint_kpts[:,1]
#         zs = joint_kpts[:,2]
#         xs = medfilt(xs, window_size)
#         ys = medfilt(ys, window_size)
#         zs = medfilt(zs, window_size)
#         filtered[joint] = np.stack([xs, ys, zs], axis = -1)

#     return filtered

def get_bone_lengths(kpts_dict):

    """
    We have to define an initial skeleton pose(T pose).
    In this case we need to known the length of each bone.
    Here we calculate the length of each bone from data
    """

    bone_lengths = {}
    for joint in kpts_dict['joints']:
        if joint == 'hips': continue
        parent = kpts_dict['hierarchy'][joint][0]

        joint_kpts = kpts_dict[joint]
        parent_kpts = kpts_dict[parent]

        _bone = joint_kpts - parent_kpts
        _bone_lengths = np.sqrt(np.sum(np.square(_bone), axis = -1))

        _bone_length = np.median(_bone_lengths)
        bone_lengths[joint] = _bone_length

        # plt.hist(bone_lengths, bins = 25)
        # plt.title(joint)
        # plt.show()

    #print(bone_lengths)
    kpts_dict['bone_lengths'] = bone_lengths
    return

#Here we define the T pose and we normalize the T pose by the length of the hips to neck distance.
def get_base_skeleton(kpts_dict, normalization_bone = 'neck'):

    #this defines a generic skeleton to which we can apply rotations to
    body_lengths = kpts_dict['bone_lengths']

    #define skeleton offset directions
    offset_directions = {}
    offset_directions['lefthip'] = np.array([1,0,0])
    offset_directions['leftknee'] = np.array([0,-1, 0])
    offset_directions['leftfoot'] = np.array([0,-1, 0])

    offset_directions['righthip'] = np.array([-1,0,0])
    offset_directions['rightknee'] = np.array([0,-1, 0])
    offset_directions['rightfoot'] = np.array([0,-1, 0])

    offset_directions['neck'] = np.array([0,1,0])

    offset_directions['leftshoulder'] = np.array([1,0,0])
    offset_directions['leftelbow'] = np.array([1,0,0])
    offset_directions['leftwrist'] = np.array([1,0,0])

    offset_directions['rightshoulder'] = np.array([-1,0,0])
    offset_directions['rightelbow'] = np.array([-1,0,0])
    offset_directions['rightwrist'] = np.array([-1,0,0])

    #set bone normalization length. Set to 1 if you dont want normalization
    normalization = kpts_dict['bone_lengths'][normalization_bone]
    #normalization = 1


    #base skeleton set by multiplying offset directions by measured bone lengths. In this case we use the average of two sided limbs. E.g left and right hip averaged
    base_skeleton = {'hips': np.array([0,0,0])}
    def _set_length(joint_type):
        base_skeleton['left' + joint_type] = offset_directions['left' + joint_type] * ((body_lengths['left' + joint_type] + body_lengths['right' + joint_type])/(2 * normalization))
        base_skeleton['right' + joint_type] = offset_directions['right' + joint_type] * ((body_lengths['left' + joint_type] + body_lengths['right' + joint_type])/(2 * normalization))

    _set_length('hip')
    _set_length('knee')
    _set_length('foot')
    _set_length('shoulder')
    _set_length('elbow')
    _set_length('wrist')
    base_skeleton['neck'] = offset_directions['neck'] * (body_lengths['neck']/normalization)

    kpts_dict['offset_directions'] = offset_directions
    kpts_dict['base_skeleton'] = base_skeleton
    kpts_dict['normalization'] = normalization

    return

#calculate the rotation of the root joint with respect to the world coordinates
def get_hips_position_and_rotation(frame_pos, root_joint = 'hips', root_define_joints = ['lefthip', 'neck']):

    #root position is saved directly
    root_position = frame_pos[root_joint]

    #calculate unit vectors of root joint
    root_u = frame_pos[root_define_joints[0]] - frame_pos[root_joint]
    root_u = root_u/np.sqrt(np.sum(np.square(root_u)))
    root_v = frame_pos[root_define_joints[1]] - frame_pos[root_joint]
    root_v = root_v/np.sqrt(np.sum(np.square(root_v)))
    root_w = np.cross(root_u, root_v)

    #Make the rotation matrix
    C = np.array([root_u, root_v, root_w]).T
    thetaz,thetay, thetax = utils.Decompose_R_ZXY(C)
    root_rotation = np.array([thetaz, thetax, thetay])

    return root_position, root_rotation

#calculate the rotation matrix and joint angles input joint
def get_joint_rotations(joint_name, joints_hierarchy, joints_offsets, frame_rotations, frame_pos):

    _invR = np.eye(3)
    for i, parent_name in enumerate(joints_hierarchy[joint_name]):
        if i == 0: continue
        _r_angles = frame_rotations[parent_name]
        R = utils.get_R_z(_r_angles[0]) @ utils.get_R_x(_r_angles[1]) @ utils.get_R_y(_r_angles[2])
        _invR = _invR@R.T

    b = _invR @ (frame_pos[joint_name] - frame_pos[joints_hierarchy[joint_name][0]])

    _R = utils.Get_R2(joints_offsets[joint_name], b)
    tz, ty, tx = utils.Decompose_R_ZXY(_R)
    joint_rs = np.array([tz, tx, ty])
    #print(np.degrees(joint_rs))

    return joint_rs

#helper function that composes a chain of rotation matrices
def get_rotation_chain(joint, hierarchy, frame_rotations):

    hierarchy = hierarchy[::-1]

    #this code assumes ZXY rotation order
    R = np.eye(3)
    for parent in hierarchy:
        angles = frame_rotations[parent][0]
        _R = utils.get_R_z(angles[0])@utils.get_R_x(angles[1])@utils.get_R_y(angles[2])
        R = R @ _R

    return R

#calculate the joint angles frame by frame.
def calculate_joint_angles(kpts_dict):

    #set up emtpy container for joint angles
    for joint in kpts_dict['joints']:
        kpts_dict[joint+'_angles'] = []

    # for framenum in range(kpts_dict['hips'].shape[0]):

        #get the keypoints positions in the current frame
    frame_pos = {}
    for joint in kpts_dict['joints']:
        frame_pos[joint] = kpts_dict[joint]

    root_position, root_rotation = get_hips_position_and_rotation(frame_pos)

    frame_rotations = {'hips': root_rotation}

    #center the body pose
    for joint in kpts_dict['joints']:
        frame_pos[joint] = frame_pos[joint] - root_position

    #get the max joints connectsion
    max_connected_joints = 0
    for joint in kpts_dict['joints']:
        if len(kpts_dict['hierarchy'][joint]) > max_connected_joints:
            max_connected_joints = len(kpts_dict['hierarchy'][joint])

    depth = 2
    while(depth <= max_connected_joints):
        for joint in kpts_dict['joints']:
            if len(kpts_dict['hierarchy'][joint]) == depth:
                joint_rs = get_joint_rotations(joint, kpts_dict['hierarchy'], kpts_dict['offset_directions'], frame_rotations, frame_pos)
                parent = kpts_dict['hierarchy'][joint][0]
                frame_rotations[parent] = joint_rs
        depth += 1

    #for completeness, add zero rotation angles for endpoints. This is not necessary as they are never used.
    for _j in kpts_dict['joints']:
        if _j not in list(frame_rotations.keys()):
            frame_rotations[_j] = np.array([0.,0.,0.])

    #update dictionary with current angles.
    for joint in kpts_dict['joints']:
        kpts_dict[joint + '_angles'].append(frame_rotations[joint])


    #convert joint angles list to numpy arrays.
    for joint in kpts_dict['joints']:
        kpts_dict[joint+'_angles'] = np.array(kpts_dict[joint + '_angles'])
        #print(joint, kpts[joint+'_angles'].shape)
    
        return

#draw the pose from original data
def draw_skeleton_from_joint_coordinates(kpts_dict):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    connections = [['hips', 'lefthip'], ['lefthip', 'leftknee'], ['leftknee', 'leftfoot'],
                   ['hips', 'righthip'], ['righthip', 'rightknee'], ['rightknee', 'rightfoot'],
                   ['hips', 'neck'], ['neck', 'leftshoulder'], ['leftshoulder', 'leftelbow'], ['leftelbow', 'leftwrist'],
                   ['neck', 'rightshoulder'], ['rightshoulder', 'rightelbow'], ['rightelbow', 'rightwrist']
                  ]

    # for framenum in range(kpts_dict['lefthip'].shape[0]):
    #     print(framenum)
    #     if framenum%2 == 0: continue #skip every 2nd frame

    for _j in kpts_dict['joints']:
        if _j == 'hips': continue
        _p = kpts_dict['hierarchy'][_j][0] #get the name of the parent joint
        r1 = kpts_dict[_p]
        r2 = kpts_dict[_j]
        plt.plot(xs = [r1[0], r2[0]], ys = [r1[1], r2[1]], zs = [r1[2], r2[2]], color = 'blue')

    #ax.set_axis_off()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    ax.set_xlim3d(-10, 10)
    ax.set_xlabel('x')
    ax.set_ylim3d(-10, 10)
    ax.set_ylabel('y')
    ax.set_zlim3d(-10, 10)
    ax.set_zlabel('z')
    plt.pause(0.1)
    ax.cla()
    plt.close()

#recalculate joint positions from calculated joint angles and draw
def draw_skeleton_from_joint_angles(kpts_dict):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')



    #get a dictionary containing the rotations for the current frame
    frame_rotations = {}
    for joint in kpts_dict['joints']:
        frame_rotations[joint] = kpts_dict[joint+'_angles']

    #for plotting
    for _j in kpts_dict['joints']:
        if _j == 'hips': continue

        #get hierarchy of how the joint connects back to root joint
        hierarchy = kpts_dict['hierarchy'][_j]

        #get the current position of the parent joint
        r1 = kpts_dict['hips']/kpts_dict['normalization']
        for parent in hierarchy:
            if parent == 'hips': continue
            R = get_rotation_chain(parent, kpts_dict['hierarchy'][parent], frame_rotations)
            r1 = r1 + R @ kpts_dict['base_skeleton'][parent]

        #get the current position of the joint. Note: r2 is the final position of the joint. r1 is simply calculated for plotting.
        r2 = r1 + get_rotation_chain(hierarchy[0], hierarchy, frame_rotations) @ kpts_dict['base_skeleton'][_j]
        plt.plot(xs = [r1[0], r2[0]], ys = [r1[1], r2[1]], zs = [r1[2], r2[2]], color = 'red')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.azim = 90
    ax.elev = -85
    ax.set_title('Pose from joint angles')
    ax.set_xlim3d(-4, 4)
    ax.set_xlabel('x')
    ax.set_ylim3d(-4, 4)
    ax.set_ylabel('y')
    ax.set_zlim3d(-4, 4)
    ax.set_zlabel('z')
    # plt.pause(0.01)
    # ax.cla()
    # plt.close()

def run(obj):
    
    kpts=obj2kpts(obj)
    # if len(sys.argv) != 2:
    #     print('Call program with input pose file')
    #     quit()

    # filename = sys.argv[1]
    # kpts = read_keypoints(filename)

    #rotate to orient the pose better
    R = utils.get_R_z(np.pi/2)
    # for framenum in range(kpts.shape[0]):
    for kpt_num in range(kpts.shape[1]):
        kpts[:,kpt_num] = R @ kpts[:,kpt_num]

    kpts_dict = convert_to_dictionary(kpts)
    add_hips_and_neck(kpts_dict)
    # filtered_kpts = median_filter(kpts_dict)
    get_bone_lengths(kpts_dict)
    get_base_skeleton(kpts_dict)

    calculate_joint_angles(kpts_dict)
    #draw_skeleton_from_joint_coordinates(filtered_kpts)
    draw_skeleton_from_joint_angles(kpts_dict)
    
    return kpts_dict