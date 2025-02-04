import sys
import logging
import json
import os
import numpy as np
import cv2
import pyzed.sl as sl
import body_keypoints
import cv_viewer.tracking_viewer as cv_viewer
import subprocess


class SVOProcessor:
    def __init__(self, svo_filepath):
        self.svo_filepath = svo_filepath
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Initializing SVOProcessor with file: %s", svo_filepath)
        
        self.zed = sl.Camera()
        self._init_zed()
        if not self.zed:
            self.logger.error("Failed to initialize ZED camera.")
            return
        
        self.body_param, self.body_runtime_param = self._init_body_tracking()
        self.camera_info = self._init_camera_info()
        self.logger.info("Initialization complete.")

    def _init_zed(self):
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD1080
        init_params.coordinate_units = sl.UNIT.METER
        init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        init_params.svo_real_time_mode = False
        init_params.set_from_svo_file(self.svo_filepath)

        if self.zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
            self.logger.error("Error opening SVO file!")
            return None
        self.logger.info("ZED camera initialized successfully.")

    
    def _init_body_tracking(self, detection_model=sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE, body_format=sl.BODY_FORMAT.BODY_18):
        body_param = sl.BodyTrackingParameters()
        body_param.enable_tracking = False
        body_param.enable_body_fitting = True
        body_param.detection_model = detection_model
        body_param.body_format = body_format
        
        self.zed.enable_body_tracking(body_param)

        body_runtime_param = sl.BodyTrackingRuntimeParameters()
        body_runtime_param.detection_confidence_threshold = 25
        body_runtime_param.skeleton_smoothing = True

        self.logger.info("Body tracking initialized successfully.")
        return body_param, body_runtime_param

    
    def _init_camera_info(self):
        camera_info = self.zed.get_camera_information()
        self.logger.info("Camera information retrieved successfully.")
        return camera_info
 
    
    def svo2json(self):
        try:
            bodies = sl.Bodies()
            image = sl.Mat()
            body_id = None

            seq_json = body_keypoints.init_json(os.path.basename(self.svo_filepath), self.camera_info, self.body_param)
            self.zed.set_svo_position(0)

            while self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_bodies(bodies, self.body_runtime_param)
                if body_id is None and len(bodies.body_list) > 0:
                    body_id = bodies.body_list[0].id

                svo_position = self.zed.get_svo_position()
                body_json = body_keypoints.get_frame_body_data(body_id, bodies, svo_position)
                if body_json["keypoint"]:
                    seq_json["seq_data"][svo_position] = body_json

            self.zed.disable_object_detection()
            self.zed.disable_positional_tracking()
            self.zed.close()

            json_filepath = self.svo_filepath.replace(".svo", ".json")
            with open(json_filepath, "w") as outfile:
                json.dump(seq_json, outfile)

            self.logger.info("SVO to JSON conversion completed successfully.")
            return json_filepath
        except Exception as e:
            self.logger.exception("Exception occurred during SVO to JSON conversion: %s", e)
            return None
    
    def svo2video(self):
        try:
            # 2D viewer utilities
            display_resolution = sl.Resolution(min(self.camera_info.camera_configuration.resolution.width, 1280),
                                            min(self.camera_info.camera_configuration.resolution.height, 720))
            image_scale = [display_resolution.width / self.camera_info.camera_configuration.resolution.width,
                        display_resolution.height / self.camera_info.camera_configuration.resolution.height]

            # Create ZED objects filled in the main loop
            bodies = sl.Bodies()
            image = sl.Mat()
        
            self.zed.set_svo_position(0)

            # Initialize Video Writer
            frame_width, frame_height = display_resolution.width, display_resolution.height
            fps = 15  # Adjust based on your input video
            #fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec for MP4 format
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # H.264 codec

            video_filepath = self.svo_filepath.replace(".svo", ".mp4")
            out = cv2.VideoWriter(video_filepath, fourcc, fps, (frame_width, frame_height))

            while self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                # Retrieve left image
                self.zed.retrieve_image(image, sl.VIEW.LEFT, sl.MEM.CPU, display_resolution)
                # Retrieve objects
                self.zed.retrieve_bodies(bodies, self.body_runtime_param)
                
                # Convert image to OpenCV format
                image_left_ocv = image.get_data()
                image_bgr = cv2.cvtColor(image_left_ocv, cv2.COLOR_BGRA2BGR)
                
                # # Render skeletons onto the image
                cv_viewer.render_2D(image_bgr, image_scale, bodies.body_list, 
                                    self.body_param.enable_tracking, self.body_param.body_format)

                # Write frame to video
                out.write(image_bgr)

            # Release Video Writer
            out.release()

            command = [
                "ffmpeg", "-y",  # Overwrite output if exists
                "-i", video_filepath,  # Input file
                "-c:v", "libx264",  # Use H.264 codec
                "-preset", "fast",  # Encoding speed vs compression
                "-crf", "23",  # Quality (lower = better, range 18-28)
                "-c:a", "aac",  # Audio codec
                "-b:a", "128k",  # Audio bitrate
                video_filepath.replace(".mp4", "_compressed.mp4")  # Output file
            ]

            # Run the command
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Disable modules and close camera
            image.free(sl.MEM.CPU)

            self.zed.disable_object_detection()
            self.zed.disable_positional_tracking()
            self.zed.close()

            self.logger.info("SVO to video conversion completed successfully.")
            return video_filepath.replace(".mp4", "_compressed.mp4")
            
        except Exception as e:
            self.logger.exception("Exception occurred during SVO to video conversion: %s", e)
            return None

if __name__ == "__main__":

    svo_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not svo_file:
        print("Usage: python svo_to_json.py <svo_file>")
    else:
        processor = SVOProcessor(svo_file)
        processor.svo2json()