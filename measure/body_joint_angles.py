#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:41:52 2023

@author: mikeszabi
"""

import pyzed.sl as sl

import numpy as np
# import sys
import utils
import body_keypoints
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


#calculate the rotation matrix and joint angles input joint
def get_joint_rotations(joint_name, joints_hierarchy, joints_offsets, centered_frame_rotations, centered_frame_pos):

    _invR = np.eye(3)
    for i, parent_name in enumerate(joints_hierarchy[joint_name]):
        if i == 0: continue
        _r_angles = centered_frame_rotations[parent_name]
        R = utils.get_R_z(_r_angles[0]) @ utils.get_R_x(_r_angles[1]) @ utils.get_R_y(_r_angles[2])
        _invR = _invR@R.T

    b = _invR @ (centered_frame_pos[joint_name] - centered_frame_pos[joints_hierarchy[joint_name][0]])

    _R = utils.Get_R2(joints_offsets[joint_name], b)
    tz, ty, tx = utils.Decompose_R_ZXY(_R)
    joint_rs = np.array([tz, tx, ty])
    #print(np.degrees(joint_rs))

    return joint_rs

#helper function that composes a chain of rotation matrices
def get_rotation_chain(joint, hierarchy, centered_frame_rotations):

    hierarchy = hierarchy[::-1]

    #this code assumes ZXY rotation order
    R = np.eye(3)
    for parent in hierarchy:
        angles = centered_frame_rotations[parent]
        _R = utils.get_R_z(angles[0])@utils.get_R_x(angles[1])@utils.get_R_y(angles[2])
        R = R @ _R

    return R

class BodyJoints:
    def __init__(self):
        
        self.ax=None
        
        self.kpts_dict={}
        
        self.bone_lengths = {}
        self.define_offset_directions()
        
            
        
    def define_offset_directions(self):
        
        self.root_joint = 'spine'
        self.endpoints=['WRIST','ANKLE']
        self.root_define_joints = ['LEFT_HIP', 'NECK']
        self.base_skeleton = {'spine': np.array([0,0,0])}
        self.normalization_bone = 'NECK'
        self.normalization=1
        
        self.offset_directions = {}
        self.offset_directions['LEFT_HIP'] = np.array([1,0,0])
        self.offset_directions['LEFT_KNEE'] = np.array([0,-1, 0])
        self.offset_directions['LEFT_ANKLE'] = np.array([0,-1, 0])

        self.offset_directions['RIGHT_HIP'] = np.array([-1,0,0])
        self.offset_directions['RIGHT_KNEE'] = np.array([0,-1, 0])
        self.offset_directions['RIGHT_ANKLE'] = np.array([0,-1, 0])

        self.offset_directions['NECK'] = np.array([0,1,0])

        self.offset_directions['LEFT_SHOULDER'] = np.array([1,0,0])
        self.offset_directions['LEFT_ELBOW'] = np.array([1,0,0])
        self.offset_directions['LEFT_WRIST'] = np.array([1,0,0])

        self.offset_directions['RIGHT_SHOULDER'] = np.array([-1,0,0])
        self.offset_directions['RIGHT_ELBOW'] = np.array([-1,0,0])
        self.offset_directions['RIGHT_WRIST'] = np.array([-1,0,0])
        

    def get_bone_lengths(self):
    
        """
        We have to define an initial skeleton pose(T pose).
        In this case we need to known the length of each bone.
        Here we calculate the length of each bone from data
        """
    
        self.bone_lengths = {}
        for joint in self.kpts_dict['joints']:
            if joint == 'spine': continue
            parent = self.kpts_dict['hierarchy'][joint][0]
    
            joint_kpts = self.kpts_dict[joint]
            parent_kpts = self.kpts_dict[parent]
    
            _bone = joint_kpts - parent_kpts
            _bone_lengths = np.sqrt(np.sum(np.square(_bone), axis = -1))
    
            _bone_length = np.median(_bone_lengths)
            self.bone_lengths[joint] = _bone_length
    
    
        return

    #Here we define the T pose and we normalize the T pose by the length of the spine to NECK distance.
    def get_base_skeleton(self):
    
        #this defines a generic skeleton to which we can apply rotations to
    
        #set bone normalization length. Set to 1 if you dont want normalization
        self.normalization = self.bone_lengths[self.normalization_bone]
        #normalization = 1
    
    
        #base skeleton set by multiplying offset directions by measured bone lengths. In this case we use the average of two sided limbs. E.g left and right hip averaged
        def _set_length(joint_type):
            self.base_skeleton['LEFT_' + joint_type] = self.offset_directions['LEFT_' + joint_type] * ((self.bone_lengths['LEFT_' + joint_type] + self.bone_lengths['RIGHT_' + joint_type])/(2 * self.normalization))
            self.base_skeleton['RIGHT_' + joint_type] = self.offset_directions['RIGHT_' + joint_type] * ((self.bone_lengths['LEFT_' + joint_type] + self.bone_lengths['RIGHT_' + joint_type])/(2 * self.normalization))
    
        _set_length('HIP')
        _set_length('KNEE')
        _set_length('ANKLE')
        _set_length('SHOULDER')
        _set_length('ELBOW')
        _set_length('WRIST')
        
        self.base_skeleton['NECK'] = self.offset_directions['NECK'] * (self.bone_lengths['NECK']/self.normalization)
    
    
        return

    #calculate the rotation of the root joint with respect to the world coordinates
    def get_spine_position_and_rotation(self,centered_frame_pos):
    
        #this is the rotation of the spine plane (neck-spine-left hip)
        self.root_position = centered_frame_pos[self.root_joint]
    
        #calculate unit vectors of root joint - LEFT HIP and NECK vectors
        root_u = centered_frame_pos[self.root_define_joints[0]] - centered_frame_pos[self.root_joint]
        root_u = root_u/np.sqrt(np.sum(np.square(root_u)))
        root_v = centered_frame_pos[self.root_define_joints[1]] - centered_frame_pos[self.root_joint]
        root_v = root_v/np.sqrt(np.sum(np.square(root_v)))
        
        root_w = np.cross(root_u, root_v)
    
        #Make the rotation matrix
        C = np.array([root_u, root_v, root_w]).T
        thetaz,thetay, thetax = utils.Decompose_R_ZXY(C)
        self.root_rotation = np.array([thetaz, thetax, thetay])
    



    #calculate the joint angles frame by frame.
    def calculate_joint_angles(self):
    
        
        centered_frame_pos = {}
   
        #set up emtpy container for joint angles
        for joint in self.kpts_dict['joints']:
            self.kpts_dict[joint+'_angles'] = []
    
    
        centered_frame_pos = {}
        for joint in self.kpts_dict['joints']:
            centered_frame_pos[joint] = self.kpts_dict[joint]
            
        # GET ROOT position and rotation
        self.get_spine_position_and_rotation(centered_frame_pos)
    
        centered_frame_rotations = {'spine': self.root_rotation}
    
        #center the body pose
        for joint in self.kpts_dict['joints']:
            centered_frame_pos[joint] = centered_frame_pos[joint] - self.root_position
    
        #get the max joints connectsion
        max_connected_joints = 0
        for joint in self.kpts_dict['joints']:
            if len(self.kpts_dict['hierarchy'][joint]) > max_connected_joints:
                max_connected_joints = len(self.kpts_dict['hierarchy'][joint])
    
        depth = 2
        while(depth <= max_connected_joints):
            for joint in self.kpts_dict['joints']:
                if len(self.kpts_dict['hierarchy'][joint]) == depth:
                    joint_rs = get_joint_rotations(joint, self.kpts_dict['hierarchy'], self.offset_directions, centered_frame_rotations, centered_frame_pos)
                    parent = self.kpts_dict['hierarchy'][joint][0]
                    centered_frame_rotations[parent] = joint_rs
            depth += 1
    
        #for completeness, add zero rotation angles for endpoints. This is not necessary as they are never used.
        for _j in self.kpts_dict['joints']:
            if _j not in list(centered_frame_rotations.keys()):
                centered_frame_rotations[_j] = np.array([0.,0.,0.])
    
        #update dictionary with current angles.
        for joint in self.kpts_dict['joints']:
            # self.kpts_dict[joint + '_angles'].append(centered_frame_rotations[joint])
            self.kpts_dict[joint + '_angles']=centered_frame_rotations[joint]
    
    
        #convert joint angles list to numpy arrays.
        for joint in self.kpts_dict['joints']:
            self.kpts_dict[joint+'_angles'] = np.array(self.kpts_dict[joint + '_angles'])
            #print(joint, kpts[joint+'_angles'].shape)
        
            return

    #draw the pose from original data
    def draw_skeleton_from_joint_coordinates(self,ax=None):
    
        if self.ax==None:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111, projection='3d')
 
        self.ax.cla()
        
        for _j in self.kpts_dict['joints']:
            self.ax.plot(self.kpts_dict[_j][0],self.kpts_dict[_j][1],self.kpts_dict[_j][2],'ro')
            
            if np.sum([e in _j for e in self.endpoints])==0: # not in endpoints
                label=np.array2string((180*self.kpts_dict[_j+'_angles']/np.pi).astype(int))               
                horizontalalignment='center'
                verticalalignment='bottom'
                if 'LEFT' in _j:
                    horizontalalignment='left'
                elif 'RIGHT' in _j:
                    horizontalalignment='right'
                if _j=='spine' or _j=='NECK':
                    verticalalignment='top'
                self.ax.text(self.kpts_dict[_j][0],self.kpts_dict[_j][1],self.kpts_dict[_j][2], # these are the coordinates to position the label
                         label,horizontalalignment=horizontalalignment,verticalalignment=verticalalignment) 
            if _j == 'spine': continue
            _p = self.kpts_dict['hierarchy'][_j][0] #get the name of the parent joint
            r1 = self.kpts_dict[_p]
            r2 = self.kpts_dict[_j]
            self.ax.plot(xs = [r1[0], r2[0]], ys = [r1[1], r2[1]], zs = [r1[2], r2[2]], color = 'blue')
    
        # ax.set_axis_off()
        self.ax.azim = -90
        self.ax.elev = 90
        # self.ax.set_xticks([])
        # self.ax.set_yticks([])
        # self.ax.set_zticks([])
    
        self.ax.set_xlim3d(-1, 1)
        self.ax.set_xlabel('x')
        self.ax.set_ylim3d(-1, 1)
        self.ax.set_ylabel('y')
        self.ax.set_zlim3d(-5, 0)
        self.ax.set_zlabel('z')
        
        plt.pause(0.001)
        return

    #recalculate joint positions from calculated joint angles and draw
    def draw_skeleton_from_joint_angles(self):
        
        if self.ax==None:
            fig = plt.figure()
            self.ax = fig.add_subplot(111, projection='3d')
        
        self.ax.cla()
            
        #get a dictionary containing the rotations for the current frame
        centered_frame_rotations = {}
        for joint in self.kpts_dict['joints']:
            centered_frame_rotations[joint] = self.kpts_dict[joint+'_angles']
    
        #for plotting
        for _j in self.kpts_dict['joints']:
            if _j == 'spine': continue
    
            #get hierarchy of how the joint connects back to root joint
            hierarchy = self.kpts_dict['hierarchy'][_j]
    
            #get the current position of the parent joint
            r1 = self.kpts_dict['spine']/self.kpts_dict['normalization']
            for parent in hierarchy:
                if parent == 'spine': continue
                R = get_rotation_chain(parent, self.kpts_dict['hierarchy'][parent], centered_frame_rotations)
                r1 = r1 + R @ self.kpts_dict['self.base_skeleton'][parent]
    
            #get the current position of the joint. Note: r2 is the final position of the joint. r1 is simply calculated for plotting.
            r2 = r1 + get_rotation_chain(hierarchy[0], hierarchy, centered_frame_rotations) @ self.kpts_dict['self.base_skeleton'][_j]
            plt.plot(xs = [r1[0], r2[0]], ys = [r1[1], r2[1]], zs = [r1[2], r2[2]], color = 'red')
    
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])
        self.ax.azim = 90
        self.ax.elev = -90
        self.ax.set_title('Pose from joint angles')
        self.ax.set_xlim3d(-1, 1)
        self.ax.set_xlabel('x')
        self.ax.set_ylim3d(-1, 1)
        self.ax.set_ylabel('y')
        self.ax.set_zlim3d(-5, 0)
        self.ax.set_zlabel('z')
        # plt.pause(0.01)
        # plt.close()

    # obj=bodies.object_list[0]
    def calculate(self,body_kpts):
        # ASSUMING ZED body18 model
        
        self.kpts=body_kpts.transpose() #obj2kpts(obj)
        # if len(sys.argv) != 2:
        #     print('Call program with input pose file')
        #     quit()
    
        # filename = sys.argv[1]
        # kpts = read_keypoints(filename)
    
        #rotate around z axis to orient the pose better - DO WE NEED THIS????
        # R_y = utils.get_R_y(np.pi/2)
        #     # # for framenum in range(kpts.shape[0]):
        #     # for kpt_num in range(kpts.shape[1]):
        #     #     kpts[:,kpt_num] = R @ kpts[:,kpt_num]
        # kpts=np.dot(R_y,kpts)
        
        self.kpts_dict=body_keypoints.keypoints_to_dict(self.kpts)
        self.kpts_dict['hierarchy'] = body_keypoints.BODY_18_definitions['hierarchy']
    
        # filtered_kpts = median_filter(self.kpts_dict)
        self.get_bone_lengths()
        self.get_base_skeleton()
    
        self.calculate_joint_angles()
        
        return self.kpts_dict

    def compare_score_bodypoints(self,body_kpts_left,body_kpts_right,visibility):
        # we do not have angles for the endpoints
        self.endpoints=['WRIST','ANKLE']
        
        kpts_left=self.calculate(body_kpts_left)
        kpts_right=self.calculate(body_kpts_right)
        
        angle_diff_score={}
     
        # visibility=np.isnan(np.sum(obj_left.keypoint,axis=1))*np.isnan(np.sum(obj_right.keypoint,axis=1))==0
       
     
        for joint in sl.BODY_18_PARTS:
            if np.sum([e in joint.name for e in self.endpoints])==0: # not in endpoints
                joint_angle_name=joint.name+'_angles'
                if joint_angle_name in kpts_left.keys() and joint_angle_name in kpts_right.keys():
                    if visibility[joint.value]:
                        left_angles=kpts_left[joint_angle_name]
                        right_angles=kpts_right[joint_angle_name]
                        
                        R1=utils.Compose_R_ZXY(left_angles[0], left_angles[1], left_angles[2])
                        R2=utils.Compose_R_ZXY(right_angles[0], right_angles[1], right_angles[2])
                        
                        diff_angle=utils.getAngle(R1, R2)
                        
                        print(joint.name)
                        print(left_angles*180/np.pi)
                        print(right_angles*180/np.pi)
    
                        angle_diff_score[joint.name]=np.cos(diff_angle)
                        print(angle_diff_score)
                
        return angle_diff_score
            
    