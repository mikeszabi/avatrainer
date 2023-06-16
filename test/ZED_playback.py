#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 08:44:29 2023

@author: itqs
"""


import sys
import pyzed.sl as sl

input_path = r'./recorded.svo' #sys.argv[0]


# Create a ZED camera object
# Set SVO path for playback
init = sl.InitParameters()
init.set_from_svo_file(input_path)


zed = sl.Camera()
status = zed.open(init)
if status != sl.ERROR_CODE.SUCCESS:
    print(repr(status))
    exit()


exit_app=False
svo_image = sl.Mat()
while not exit_app:
  if zed.grab() == sl.ERROR_CODE.SUCCESS:
    # Read side by side frames stored in the SVO
    zed.retrieve_image(svo_image, sl.VIEW.SIDE_BY_SIDE)
    # Get frame count
    svo_position = zed.get_svo_position();
  elif zed.grab() == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
    print("SVO end has been reached. Looping back to first frame")
    zed.set_svo_position(0)
    exit_app=True