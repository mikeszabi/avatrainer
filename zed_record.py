#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 08:34:11 2023

@author: itqs
"""
# https://www.stereolabs.com/docs/video/recording/

import sys
import pyzed.sl as sl

# Create a ZED camera object
init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD2K,
                             depth_mode=sl.DEPTH_MODE.ULTRA,
                             coordinate_units=sl.UNIT.METER,
                             coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
zed = sl.Camera()
status = zed.open(init)
if status != sl.ERROR_CODE.SUCCESS:
    print(repr(status))
    exit()

# Enable recording with the filename specified in argument
output_path = r'./recorded.svo' #sys.argv[0]
recordingParameters = sl.RecordingParameters()
recordingParameters.compression_mode = sl.SVO_COMPRESSION_MODE.H264
recordingParameters.video_filename = output_path
err = zed.enable_recording(recordingParameters)

i=0
while not i>100: #exit_app:
    # Each new frame is added to the SVO file
    zed.grab()
    i=i+1

# Disable recording
zed.disable_recording()