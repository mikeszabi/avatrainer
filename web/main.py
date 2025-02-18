# uvicorn main:app --reload

from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil
import os
import json
import numpy as np
import pyzed.sl as sl

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload_svo/")
async def upload_svo(file: UploadFile = File(...)):
    """Fogad egy SVO fájlt és elmenti."""
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded successfully", "file_path": file_location}


def extract_skeleton_from_svo(svo_path: str):
    """Feldolgozza az SVO fájlt és kivonja az ízületi kulcspontokat."""

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_path)  # Ensure the SVO file path is set
    init_params.svo_real_time_mode = False
    init_params.camera_resolution = sl.RESOLUTION.HD1080  # Use HD1080 video mode
    init_params.coordinate_units = sl.UNIT.METER          # Set coordinate units
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    zed = sl.Camera()
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        return {"error": f"Failed to open SVO file: {err}"}
    
    # Enable Positional tracking (mandatory for object detection)
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    positional_tracking_parameters.set_as_static = True
    zed.enable_positional_tracking(positional_tracking_parameters)
    
    # Emberi csontváz felismerési modul inicializálása
    body_params = sl.BodyTrackingParameters()
    body_params.enable_tracking = True
    body_params.enable_body_fitting = True
    body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE
    body_params.body_format = sl.BODY_FORMAT.BODY_18  # Choose the BODY_FORMAT you wish to use

    zed.enable_body_tracking(body_params)

    # Adatok inicializálása
    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 25
    body_runtime_param.skeleton_smoothing = True

    runtime_params = sl.RuntimeParameters()
    bodies = sl.Bodies()
    
    skeleton_data = []
    
    while zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
        # Csontváz adatok kiolvasása
        zed.retrieve_bodies(bodies, body_runtime_param)
        
        for body in bodies.body_list:
            if body.tracking_state == sl.OBJECT_TRACKING_STATE.OK:
                joints = np.array([[joint[0], joint[1], joint[2]] 
                                   for joint in body.keypoint if joint is not None]).tolist()
                skeleton_data.append(joints)
    
    zed.close()
    
    # JSON export
    output_json = os.path.join(UPLOAD_FOLDER, os.path.basename(svo_path) + "_skeleton.json")
    with open(output_json, "w") as f:
        json.dump(skeleton_data, f)
    
    return {"message": "Skeleton extracted", "output_file": output_json}


@app.get("/process_svo/{filename}")
def process_svo(filename: str):
    """Feldolgozza a feltöltött SVO fájlt és visszaküldi a csontvázadatokat JSON-ben."""
    svo_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(svo_path):
        return {"error": "File not found"}
    
    result = extract_skeleton_from_svo(svo_path)
    
    return result


@app.get("/get_skeleton/{filename}")
def get_skeleton(filename: str):
    """Visszaadja a már feldolgozott skeleton JSON fájlt."""
    json_path = os.path.join(UPLOAD_FOLDER, filename + "_skeleton.json")
    
    if not os.path.exists(json_path):
        return {"error": "Skeleton file not found"}
    
    with open(json_path, "r") as f:
        data = json.load(f)
    
    return {"skeleton": data}

app.mount("/public", StaticFiles(directory="public"), name="public")
