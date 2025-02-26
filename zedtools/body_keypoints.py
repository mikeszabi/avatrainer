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

BODY_34_definitions = {'keypoints_to_index': {
                    'PELVIS':         sl.BODY_34_PARTS.PELVIS.value,
                    'NAVAL_SPINE':    sl.BODY_34_PARTS.NAVAL_SPINE.value,
                    'CHEST_SPINE':    sl.BODY_34_PARTS.CHEST_SPINE.value,
                    'NECK':           sl.BODY_34_PARTS.NECK.value,
                    'LEFT_CLAVICLE':  sl.BODY_34_PARTS.LEFT_CLAVICLE.value,
                    'LEFT_SHOULDER':  sl.BODY_34_PARTS.LEFT_SHOULDER.value,
                    'LEFT_ELBOW':     sl.BODY_34_PARTS.LEFT_ELBOW.value,
                    'LEFT_WRIST':     sl.BODY_34_PARTS.LEFT_WRIST.value,
                    'LEFT_HAND':      sl.BODY_34_PARTS.LEFT_HAND.value,
                    'LEFT_HANDTIP':   sl.BODY_34_PARTS.LEFT_HANDTIP.value,
                    'LEFT_THUMB':     sl.BODY_34_PARTS.LEFT_THUMB.value,
                    'RIGHT_CLAVICLE': sl.BODY_34_PARTS.RIGHT_CLAVICLE.value,
                    'RIGHT_SHOULDER': sl.BODY_34_PARTS.RIGHT_SHOULDER.value,
                    'RIGHT_ELBOW':    sl.BODY_34_PARTS.RIGHT_ELBOW.value,
                    'RIGHT_WRIST':    sl.BODY_34_PARTS.RIGHT_WRIST.value,
                    'RIGHT_HAND':     sl.BODY_34_PARTS.RIGHT_HAND.value,
                    'RIGHT_HANDTIP':  sl.BODY_34_PARTS.RIGHT_HANDTIP.value,
                    'RIGHT_THUMB':    sl.BODY_34_PARTS.RIGHT_THUMB.value,
                    'LEFT_HIP':       sl.BODY_34_PARTS.LEFT_HIP.value,
                    'LEFT_KNEE':      sl.BODY_34_PARTS.LEFT_KNEE.value,
                    'LEFT_ANKLE':     sl.BODY_34_PARTS.LEFT_ANKLE.value,
                    'LEFT_FOOT':      sl.BODY_34_PARTS.LEFT_FOOT.value,
                    'RIGHT_HIP':      sl.BODY_34_PARTS.RIGHT_HIP.value,
                    'RIGHT_KNEE':     sl.BODY_34_PARTS.RIGHT_KNEE.value,
                    'RIGHT_ANKLE':    sl.BODY_34_PARTS.RIGHT_ANKLE.value,
                    'RIGHT_FOOT':     sl.BODY_34_PARTS.RIGHT_FOOT.value,
                    'HEAD':           sl.BODY_34_PARTS.HEAD.value,
                    'NOSE':           sl.BODY_34_PARTS.NOSE.value,
                    'LEFT_EYE':       sl.BODY_34_PARTS.LEFT_EYE.value,
                    'LEFT_EAR':       sl.BODY_34_PARTS.LEFT_EAR.value,
                    'RIGHT_EYE':      sl.BODY_34_PARTS.RIGHT_EYE.value,
                    'RIGHT_EAR':      sl.BODY_34_PARTS.RIGHT_EAR.value,
                    'LEFT_HEEL':      sl.BODY_34_PARTS.LEFT_HEEL.value,
                    'RIGHT_HEEL':     sl.BODY_34_PARTS.RIGHT_HEEL.value,
                    'LAST':           sl.BODY_34_PARTS.LAST.value,
                },
                'keypoints_relevancy': {
                    'PELVIS':         100,
                    'NAVAL_SPINE':    100,
                    'CHEST_SPINE':    100,
                    'NECK':           100,
                    'LEFT_CLAVICLE':  100,
                    'LEFT_SHOULDER':  100,
                    'LEFT_ELBOW':     100,
                    'LEFT_WRIST':     100,
                    'LEFT_HAND':      100,
                    'LEFT_HANDTIP':   100,
                    'LEFT_THUMB':     100,
                    'RIGHT_CLAVICLE': 100,
                    'RIGHT_SHOULDER': 100,
                    'RIGHT_ELBOW':    100,
                    'RIGHT_WRIST':    100,
                    'RIGHT_HAND':     100,
                    'RIGHT_HANDTIP':  100,
                    'RIGHT_THUMB':    100,
                    'LEFT_HIP':       100,
                    'LEFT_KNEE':      100,
                    'LEFT_ANKLE':     100,
                    'LEFT_FOOT':      100,
                    'RIGHT_HIP':      100,
                    'RIGHT_KNEE':     100,
                    'RIGHT_ANKLE':    100,
                    'RIGHT_FOOT':     100,
                    'HEAD':           100,
                    'NOSE':           0,
                    'LEFT_EYE':       0,
                    'LEFT_EAR':       0,
                    'RIGHT_EYE':      0,
                    'RIGHT_EAR':      0,
                    'LEFT_HEEL':      100,
                    'RIGHT_HEEL':     100,
                    'LAST':           0,
                },
                'hierarchy': {
                    'PELVIS':         [],
                    'NAVAL_SPINE':    ['PELVIS'],
                    'CHEST_SPINE':    ['NAVAL_SPINE', 'PELVIS'],
                    'NECK':           ['CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'HEAD':           ['NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'NOSE':           ['HEAD', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_EYE':       ['NOSE', 'HEAD', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_EAR':       ['LEFT_EYE', 'NOSE', 'HEAD', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_EYE':      ['NOSE', 'HEAD', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_EAR':      ['RIGHT_EYE', 'NOSE', 'HEAD', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_CLAVICLE':  ['NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_SHOULDER':  ['LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_ELBOW':     ['LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_WRIST':     ['LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_HAND':      ['LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_HANDTIP':   ['LEFT_HAND', 'LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_THUMB':     ['LEFT_HAND', 'LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_CLAVICLE': ['NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_SHOULDER': ['RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_ELBOW':    ['RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_WRIST':    ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_HAND':     ['RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_HANDTIP':  ['RIGHT_HAND', 'RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'RIGHT_THUMB':    ['RIGHT_HAND', 'RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK', 'CHEST_SPINE', 'NAVAL_SPINE', 'PELVIS'],
                    'LEFT_HIP':       ['PELVIS'],
                    'LEFT_KNEE':      ['LEFT_HIP', 'PELVIS'],
                    'LEFT_ANKLE':     ['LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'LEFT_FOOT':      ['LEFT_ANKLE', 'LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'LEFT_HEEL':      ['LEFT_ANKLE', 'LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'RIGHT_HIP':      ['PELVIS'],
                    'RIGHT_KNEE':     ['RIGHT_HIP', 'PELVIS'],
                    'RIGHT_ANKLE':    ['RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'RIGHT_FOOT':     ['RIGHT_ANKLE', 'RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'RIGHT_HEEL':     ['RIGHT_ANKLE', 'RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'LAST':           []
                },
                'connections': [
                    # Central body
                    ['PELVIS', 'NAVAL_SPINE'],
                    ['NAVAL_SPINE', 'CHEST_SPINE'],
                    ['CHEST_SPINE', 'NECK'],
                    ['NECK', 'HEAD'],
                    ['HEAD', 'NOSE'],
                    # Facial features
                    ['NOSE', 'LEFT_EYE'],
                    ['LEFT_EYE', 'LEFT_EAR'],
                    ['NOSE', 'RIGHT_EYE'],
                    ['RIGHT_EYE', 'RIGHT_EAR'],
                    # Left arm
                    ['NECK', 'LEFT_CLAVICLE'],
                    ['LEFT_CLAVICLE', 'LEFT_SHOULDER'],
                    ['LEFT_SHOULDER', 'LEFT_ELBOW'],
                    ['LEFT_ELBOW', 'LEFT_WRIST'],
                    ['LEFT_WRIST', 'LEFT_HAND'],
                    ['LEFT_HAND', 'LEFT_HANDTIP'],
                    ['LEFT_HAND', 'LEFT_THUMB'],
                    # Right arm
                    ['NECK', 'RIGHT_CLAVICLE'],
                    ['RIGHT_CLAVICLE', 'RIGHT_SHOULDER'],
                    ['RIGHT_SHOULDER', 'RIGHT_ELBOW'],
                    ['RIGHT_ELBOW', 'RIGHT_WRIST'],
                    ['RIGHT_WRIST', 'RIGHT_HAND'],
                    ['RIGHT_HAND', 'RIGHT_HANDTIP'],
                    ['RIGHT_HAND', 'RIGHT_THUMB'],
                    # Left leg
                    ['PELVIS', 'LEFT_HIP'],
                    ['LEFT_HIP', 'LEFT_KNEE'],
                    ['LEFT_KNEE', 'LEFT_ANKLE'],
                    ['LEFT_ANKLE', 'LEFT_FOOT'],
                    ['LEFT_ANKLE', 'LEFT_HEEL'],
                    # Right leg
                    ['PELVIS', 'RIGHT_HIP'],
                    ['RIGHT_HIP', 'RIGHT_KNEE'],
                    ['RIGHT_KNEE', 'RIGHT_ANKLE'],
                    ['RIGHT_ANKLE', 'RIGHT_FOOT'],
                    ['RIGHT_ANKLE', 'RIGHT_HEEL'],
                ]
}

BODY_38_definitions = {'keypoints_to_index': {
                    'PELVIS':             sl.BODY_38_PARTS.PELVIS.value,
                    'SPINE_1':            sl.BODY_38_PARTS.SPINE_1.value,
                    'SPINE_2':            sl.BODY_38_PARTS.SPINE_2.value,
                    'SPINE_3':            sl.BODY_38_PARTS.SPINE_3.value,
                    'NECK':               sl.BODY_38_PARTS.NECK.value,
                    'NOSE':               sl.BODY_38_PARTS.NOSE.value,
                    'LEFT_EYE':           sl.BODY_38_PARTS.LEFT_EYE.value,
                    'RIGHT_EYE':          sl.BODY_38_PARTS.RIGHT_EYE.value,
                    'LEFT_EAR':           sl.BODY_38_PARTS.LEFT_EAR.value,
                    'RIGHT_EAR':          sl.BODY_38_PARTS.RIGHT_EAR.value,
                    'LEFT_CLAVICLE':      sl.BODY_38_PARTS.LEFT_CLAVICLE.value,
                    'RIGHT_CLAVICLE':     sl.BODY_38_PARTS.RIGHT_CLAVICLE.value,
                    'LEFT_SHOULDER':      sl.BODY_38_PARTS.LEFT_SHOULDER.value,
                    'RIGHT_SHOULDER':     sl.BODY_38_PARTS.RIGHT_SHOULDER.value,
                    'LEFT_ELBOW':         sl.BODY_38_PARTS.LEFT_ELBOW.value,
                    'RIGHT_ELBOW':        sl.BODY_38_PARTS.RIGHT_ELBOW.value,
                    'LEFT_WRIST':         sl.BODY_38_PARTS.LEFT_WRIST.value,
                    'RIGHT_WRIST':        sl.BODY_38_PARTS.RIGHT_WRIST.value,
                    'LEFT_HIP':           sl.BODY_38_PARTS.LEFT_HIP.value,
                    'RIGHT_HIP':          sl.BODY_38_PARTS.RIGHT_HIP.value,
                    'LEFT_KNEE':          sl.BODY_38_PARTS.LEFT_KNEE.value,
                    'RIGHT_KNEE':         sl.BODY_38_PARTS.RIGHT_KNEE.value,
                    'LEFT_ANKLE':         sl.BODY_38_PARTS.LEFT_ANKLE.value,
                    'RIGHT_ANKLE':        sl.BODY_38_PARTS.RIGHT_ANKLE.value,
                    'LEFT_BIG_TOE':       sl.BODY_38_PARTS.LEFT_BIG_TOE.value,
                    'RIGHT_BIG_TOE':      sl.BODY_38_PARTS.RIGHT_BIG_TOE.value,
                    'LEFT_SMALL_TOE':     sl.BODY_38_PARTS.LEFT_SMALL_TOE.value,
                    'RIGHT_SMALL_TOE':    sl.BODY_38_PARTS.RIGHT_SMALL_TOE.value,
                    'LEFT_HEEL':          sl.BODY_38_PARTS.LEFT_HEEL.value,
                    'RIGHT_HEEL':         sl.BODY_38_PARTS.RIGHT_HEEL.value,
                    'LEFT_HAND_THUMB_4':  sl.BODY_38_PARTS.LEFT_HAND_THUMB_4.value,
                    'RIGHT_HAND_THUMB_4': sl.BODY_38_PARTS.RIGHT_HAND_THUMB_4.value,
                    'LEFT_HAND_INDEX_1':  sl.BODY_38_PARTS.LEFT_HAND_INDEX_1.value,
                    'RIGHT_HAND_INDEX_1': sl.BODY_38_PARTS.RIGHT_HAND_INDEX_1.value,
                    'LEFT_HAND_MIDDLE_4': sl.BODY_38_PARTS.LEFT_HAND_MIDDLE_4.value,
                    'RIGHT_HAND_MIDDLE_4':sl.BODY_38_PARTS.RIGHT_HAND_MIDDLE_4.value,
                    'LEFT_HAND_PINKY_1':  sl.BODY_38_PARTS.LEFT_HAND_PINKY_1.value,
                    'RIGHT_HAND_PINKY_1': sl.BODY_38_PARTS.RIGHT_HAND_PINKY_1.value,
                    'LAST':               sl.BODY_38_PARTS.LAST.value,
                },
                'keypoints_relevancy': {
                    'PELVIS':             100,
                    'SPINE_1':            100,
                    'SPINE_2':            100,
                    'SPINE_3':            100,
                    'NECK':               100,
                    'NOSE':               100,
                    'LEFT_EYE':           100,
                    'RIGHT_EYE':          100,
                    'LEFT_EAR':           100,
                    'RIGHT_EAR':          100,
                    'LEFT_CLAVICLE':      100,
                    'RIGHT_CLAVICLE':     100,
                    'LEFT_SHOULDER':      100,
                    'RIGHT_SHOULDER':     100,
                    'LEFT_ELBOW':         100,
                    'RIGHT_ELBOW':        100,
                    'LEFT_WRIST':         100,
                    'RIGHT_WRIST':        100,
                    'LEFT_HIP':           100,
                    'RIGHT_HIP':          100,
                    'LEFT_KNEE':          100,
                    'RIGHT_KNEE':         100,
                    'LEFT_ANKLE':         100,
                    'RIGHT_ANKLE':        100,
                    'LEFT_BIG_TOE':       100,
                    'RIGHT_BIG_TOE':      100,
                    'LEFT_SMALL_TOE':     100,
                    'RIGHT_SMALL_TOE':    100,
                    'LEFT_HEEL':          100,
                    'RIGHT_HEEL':         100,
                    'LEFT_HAND_THUMB_4':  100,
                    'RIGHT_HAND_THUMB_4': 100,
                    'LEFT_HAND_INDEX_1':  100,
                    'RIGHT_HAND_INDEX_1': 100,
                    'LEFT_HAND_MIDDLE_4': 100,
                    'RIGHT_HAND_MIDDLE_4':100,
                    'LEFT_HAND_PINKY_1':  100,
                    'RIGHT_HAND_PINKY_1': 100,
                    'LAST':               100,
                },
                'hierarchy': {
                    # Central Body
                    'PELVIS':      [],
                    'SPINE_1':     ['PELVIS'],
                    'SPINE_2':     ['SPINE_1', 'PELVIS'],
                    'SPINE_3':     ['SPINE_2', 'SPINE_1', 'PELVIS'],
                    'NECK':        ['SPINE_3', 'SPINE_2', 'SPINE_1', 'PELVIS'],
                    # Face: Attach facial keypoints to NECK/NOSE
                    'NOSE':        ['NECK'],
                    'LEFT_EYE':    ['NOSE'],
                    'RIGHT_EYE':   ['NOSE'],
                    'LEFT_EAR':    ['LEFT_EYE', 'NOSE'],
                    'RIGHT_EAR':   ['RIGHT_EYE', 'NOSE'],
                    # Left Arm
                    'LEFT_CLAVICLE': ['NECK'],
                    'LEFT_SHOULDER': ['LEFT_CLAVICLE', 'NECK'],
                    'LEFT_ELBOW':    ['LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    'LEFT_WRIST':    ['LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    'LEFT_HAND_THUMB_4':  ['LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    'LEFT_HAND_INDEX_1':  ['LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    'LEFT_HAND_MIDDLE_4': ['LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    'LEFT_HAND_PINKY_1':  ['LEFT_WRIST', 'LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_CLAVICLE', 'NECK'],
                    # Right Arm
                    'RIGHT_CLAVICLE': ['NECK'],
                    'RIGHT_SHOULDER': ['RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_ELBOW':    ['RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_WRIST':    ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_HAND_THUMB_4':  ['RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_HAND_INDEX_1':  ['RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_HAND_MIDDLE_4': ['RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    'RIGHT_HAND_PINKY_1':  ['RIGHT_WRIST', 'RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_CLAVICLE', 'NECK'],
                    # Left Leg
                    'LEFT_HIP':    ['PELVIS'],
                    'LEFT_KNEE':   ['LEFT_HIP', 'PELVIS'],
                    'LEFT_ANKLE':  ['LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'LEFT_BIG_TOE':   ['LEFT_ANKLE', 'LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'LEFT_SMALL_TOE': ['LEFT_ANKLE', 'LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    'LEFT_HEEL':      ['LEFT_ANKLE', 'LEFT_KNEE', 'LEFT_HIP', 'PELVIS'],
                    # Right Leg
                    'RIGHT_HIP':   ['PELVIS'],
                    'RIGHT_KNEE':  ['RIGHT_HIP', 'PELVIS'],
                    'RIGHT_ANKLE': ['RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'RIGHT_BIG_TOE':   ['RIGHT_ANKLE', 'RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'RIGHT_SMALL_TOE': ['RIGHT_ANKLE', 'RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    'RIGHT_HEEL':      ['RIGHT_ANKLE', 'RIGHT_KNEE', 'RIGHT_HIP', 'PELVIS'],
                    # LAST marker: no hierarchy
                    'LAST':       []
                },
                'connections': [
                    # Spine and Central Body
                    ['PELVIS', 'SPINE_1'],
                    ['SPINE_1', 'SPINE_2'],
                    ['SPINE_2', 'SPINE_3'],
                    ['SPINE_3', 'NECK'],
                    ['NECK', 'NOSE'],
                    # Facial Features
                    ['NOSE', 'LEFT_EYE'],
                    ['NOSE', 'RIGHT_EYE'],
                    ['LEFT_EYE', 'LEFT_EAR'],
                    ['RIGHT_EYE', 'RIGHT_EAR'],
                    # Left Arm
                    ['NECK', 'LEFT_CLAVICLE'],
                    ['LEFT_CLAVICLE', 'LEFT_SHOULDER'],
                    ['LEFT_SHOULDER', 'LEFT_ELBOW'],
                    ['LEFT_ELBOW', 'LEFT_WRIST'],
                    ['LEFT_WRIST', 'LEFT_HAND_THUMB_4'],
                    ['LEFT_WRIST', 'LEFT_HAND_INDEX_1'],
                    ['LEFT_WRIST', 'LEFT_HAND_MIDDLE_4'],
                    ['LEFT_WRIST', 'LEFT_HAND_PINKY_1'],
                    # Right Arm
                    ['NECK', 'RIGHT_CLAVICLE'],
                    ['RIGHT_CLAVICLE', 'RIGHT_SHOULDER'],
                    ['RIGHT_SHOULDER', 'RIGHT_ELBOW'],
                    ['RIGHT_ELBOW', 'RIGHT_WRIST'],
                    ['RIGHT_WRIST', 'RIGHT_HAND_THUMB_4'],
                    ['RIGHT_WRIST', 'RIGHT_HAND_INDEX_1'],
                    ['RIGHT_WRIST', 'RIGHT_HAND_MIDDLE_4'],
                    ['RIGHT_WRIST', 'RIGHT_HAND_PINKY_1'],
                    # Left Leg
                    ['PELVIS', 'LEFT_HIP'],
                    ['LEFT_HIP', 'LEFT_KNEE'],
                    ['LEFT_KNEE', 'LEFT_ANKLE'],
                    ['LEFT_ANKLE', 'LEFT_BIG_TOE'],
                    ['LEFT_ANKLE', 'LEFT_SMALL_TOE'],
                    ['LEFT_ANKLE', 'LEFT_HEEL'],
                    # Right Leg
                    ['PELVIS', 'RIGHT_HIP'],
                    ['RIGHT_HIP', 'RIGHT_KNEE'],
                    ['RIGHT_KNEE', 'RIGHT_ANKLE'],
                    ['RIGHT_ANKLE', 'RIGHT_BIG_TOE'],
                    ['RIGHT_ANKLE', 'RIGHT_SMALL_TOE'],
                    ['RIGHT_ANKLE', 'RIGHT_HEEL'],
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


    
def keypoints_18_to_dict(kpts,keypoints_to_index=BODY_18_definitions['keypoints_to_index']):
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

def keypoints_34_to_dict(kpts,keypoints_to_index=BODY_34_definitions['keypoints_to_index']):
    # using ZED's convention
    # its easier to manipulate keypoints by joint name
    # kpts: 3x34 keypoint matrix
   
    kpts_dict = {}
    kpts_dict['joints']=[]
    for key, k_index in keypoints_to_index.items():
        if key not in ['NOSE']:
            if k_index<kpts.shape[1]:
                kpts_dict[key] = kpts[:,k_index]
                kpts_dict['joints'].append(key)
    
    kpts_dict['root_joint'] = 'NAVAL_SPINE'

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
    
    
