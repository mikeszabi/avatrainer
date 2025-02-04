import sys
sys.path.append(r'../zedtools')
import cv2
import pyzed.sl as sl
import body_keypoints
import cv_viewer.tracking_viewer as cv_viewer

import numpy as np
import os
from svo_processor import SVOProcessor

svo_file=r'../store/biceps_cur_1_2023_06_23_11_16_25_cut.svo'

#processor = SVOProcessor(svo_file)
#processor.svo2json()

processor = SVOProcessor(svo_file)
if processor is None:
    raise ValueError("Processor initialization returned None")
#processor.svo2video()


camera_info=processor.camera_info

# 2D viewer utilities
display_resolution = sl.Resolution(min(camera_info.camera_configuration.resolution.width, 1280),
                                min(camera_info.camera_configuration.resolution.height, 720))
image_scale = [display_resolution.width / camera_info.camera_configuration.resolution.width,
            display_resolution.height / camera_info.camera_configuration.resolution.height]

# Create ZED objects filled in the main loop
bodies = sl.Bodies()
image = sl.Mat()

processor.zed.set_svo_position(0)

# Initialize Video Writer
frame_width, frame_height = display_resolution.width, display_resolution.height
fps = 15  # Adjust based on your input video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for MP4 format

video_filepath = processor.svo_filepath.replace(".svo", ".mp4")
out = cv2.VideoWriter(
        video_filepath,
        fourcc,
        15,
        (frame_width, frame_height)
    )

while processor.zed.grab() == sl.ERROR_CODE.SUCCESS:
    # Retrieve left image
    processor.zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
    # Retrieve objects
    processor.zed.retrieve_bodies(bodies, processor.body_runtime_param)
    
    # Convert image to OpenCV format
    image_left_ocv = image.get_data().copy()
    image_bgr = cv2.cvtColor(image_left_ocv, cv2.COLOR_BGRA2BGR)
    
    # # Render skeletons onto the image
    cv_viewer.render_2D(image_bgr, image_scale, bodies.body_list, 
        processor.body_param.enable_tracking, processor.body_param.body_format)

 

    # Write frame to video
    out.write(image_bgr)



    # Write frame to video
    out.write(image_bgr)

    

# Release Video Writer
out.release()


# Disable modules and close camera
processor.zed.disable_object_detection()
processor.zed.disable_positional_tracking()
processor.zed.close()
processor.image.free(sl.MEM.CPU)
