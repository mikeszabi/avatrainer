import * as THREE from 'three';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'; // Import OrbitControls


const keypoints_to_index = {
    "NOSE": 0, "NECK": 1, "RIGHT_SHOULDER": 2, "RIGHT_ELBOW": 3, "RIGHT_WRIST": 4,
    "LEFT_SHOULDER": 5, "LEFT_ELBOW": 6, "LEFT_WRIST": 7, "RIGHT_HIP": 8, "RIGHT_KNEE": 9,
    "RIGHT_ANKLE": 10, "LEFT_HIP": 11, "LEFT_KNEE": 12, "LEFT_ANKLE": 13, "RIGHT_EYE": 14,
    "LEFT_EYE": 15, "RIGHT_EAR": 16, "LEFT_EAR": 17, "spine": 18
};

const boneNamesToKeypoints = {
    //'mixamorigNeck': 'NOSE',
    "mixamorigNeck": "NECK",
    "mixamorigLeftUpLeg": "LEFT_HIP",
    "mixamorigRightUpLeg": "RIGHT_HIP",
    "mixamorigRightLeg": "RIGHT_KNEE",
    "mixamorigLeftLeg": "LEFT_KNEE",
    "mixamorigRightFoot": "RIGHT_ANKLE",
    "mixamorigLeftFoot": "LEFT_ANKLE",
    "mixamorigLeftHand": "LEFT_WRIST",
    "mixamorigLeftForeArm": "LEFT_ELBOW",
    "mixamorigLeftArm": "LEFT_SHOULDER",
    "mixamorigRightArm": "RIGHT_SHOULDER",
    //"mixamorigLeftArm": "LEFT_SHOULDER",
    "mixamorigRightHand": "RIGHT_WRIST",
    "mixamorigRightForeArm": "RIGHT_ELBOW",
    //"mixamorigRightArm": "RIGHT_SHOULDER",
};

var iks = [];
var boneLength = {};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setClearColor(0x003333); // Dark teal
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, -5).normalize();
scene.add(directionalLight);

const loader = new FBXLoader();
let skeleton;

function moveBoneToWorldPosition(bone, worldPosition) {
    const localPosition = new THREE.Vector3();
    bone.parent.worldToLocal(localPosition.copy(worldPosition));
    bone.position.lerp(localPosition, 0.5);
    bone.updateMatrixWorld();
}

function midPoint(boneName1, boneName2, global_positions, ratio = [1, 1]) {
    let worldPosition1 =global_positions[boneName1];
    let worldPosition2 = global_positions[boneName2];
    let midpoint = new THREE.Vector3().addVectors(worldPosition1.clone().multiplyScalar(ratio[0]), worldPosition2.clone().multiplyScalar(ratio[1])).multiplyScalar(1 / (ratio[0] + ratio[1]));
    return midpoint;
}


let bone_dict = {}

var base = {};
var i = 10;
function setupIK(model) {
    const skeleton = model.skeleton;

    if (!skeleton || !skeleton.bones) {
        console.error("Skeleton is missing or does not contain bones!");
        return;
    }

    let clock = new THREE.Clock();
    let delta = 0;
    const interval = 1 / 30;

    function animate() {
        requestAnimationFrame(animate);

        delta += clock.getDelta();

        if (delta > interval) {
            i = (i + 1) % keypoints.seq_data.length;
            logBonePositions(model);
            updateSkeleton(keypoints.seq_data[i].keypoint);

            delta = delta % interval;
        }
        controls.update();
        renderer.render(scene, camera);
    }

    animate();
   
}

var keypoints = null;

camera.position.set(0, 0, -5);
camera.lookAt(0, 1, 0);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.25;
controls.screenSpacePanning = false;
controls.minDistance = 1;
controls.maxDistance = 100;
controls.maxPolarAngle = Math.PI / 2;

controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.PAN
};

function printBoneNames(object) {
    object.traverse(function (child) {
        if (child.isBone) {
            console.log(child.name);
            const name = child.name;
            const lastUnderscoreIndex = name.lastUnderscoreIndex;
            if (lastUnderscoreIndex !== -1) {
                const key = name.substring(0, lastUnderscoreIndex);
                const value = name.substring(lastUnderscoreIndex);
                bone_dict[key] = value;
            }
        }
    });
}

function logBonePositions(model) {
    model.skeleton.bones.forEach((bone, index) => {
        const localPosition = bone.position;
        const length = localPosition.length();
        if(!boneLength.hasOwnProperty(bone.name))
            boneLength[bone.name] = length;
        if (isNaN(localPosition.x) || isNaN(localPosition.y) || isNaN(localPosition.z)) {
            console.warn(`❌ Bone ${bone.name} (index: ${index}) has NaN position!`, localPosition);
        }
    });
}

// Update JSON loading functions
function getJsonPath() {
    const params = new URLSearchParams(window.location.search);
    return params.get('jsonPath') || 'json/complex1_HD1080_SN30195290_12-40-11_smooth.json'; // Default path updated
}

function loadJSON(callback) {
    const jsonPath = window.ANIMATION_JSON_PATH;
    console.log('Loading JSON from:', jsonPath);
    
    fetch(jsonPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(jsonString => {
            // Replace NaN values with 0
            jsonString = jsonString.replace(/NaN/g, '0');
            const data = JSON.parse(jsonString);
            data.seq_data = Object.values(data.seq_data);
            callback(data);
        })
        .catch(error => {
            console.error('Error loading JSON:', error);
            console.error('Attempted to load from:', jsonPath);
        });
}

// Start animation only after JSON is loaded
function initAnimation(data) {
    keypoints = data;
    console.log('Loaded keypoints data:', data);
    
    // Load FBX model after JSON is loaded
    loader.load('amy.fbx', function (fbx) {
        skeleton = fbx;
        skeleton.scale.set(0.015, 0.015, 0.015);
        skeleton.rotation.y = -Math.PI / 4;
        scene.add(skeleton);
        const skeletonHelper = new THREE.SkeletonHelper(skeleton);
        scene.add(skeletonHelper);
        printBoneNames(skeleton);

        let skinnedMesh = undefined;
        skeleton.traverse((bone) => {
            if (bone.isSkinnedMesh && !skinnedMesh) {
                skinnedMesh = bone;
                console.log('Found skinned mesh:', bone.name);
            }
        });
        setupIK(skinnedMesh);
    });
}

// Load JSON and initialize
loadJSON(initAnimation);

function normalizeLength(boneName) {
    let bone = skeleton.getObjectByName(boneName);
    let length = boneLength[boneName];
    let ratio = length / bone.position.length();
    //console.log("ration:", ratio);
    let p = bone.position.multiplyScalar(ratio);

    if(!(isNaN(p.x) || isNaN(p.y) || isNaN(p.z)))
        bone.position.set( p.x, p.y, p.z );
    bone.updateMatrixWorld();
}

function rotateParentBasedOnChild(parentName, global_positions, base = undefined) {
    let parent = skeleton.getObjectByName(parentName);

    let parentparent = parent.parent;
    scene.attach(parent);
    let child = parent.children[parent.children.length - 1];
    let childName = child.name;
    let childPosition = global_positions[childName];
    let parentPosition = global_positions[parentName];
    let direction = childPosition.clone().sub(parentPosition).normalize();
    
    let quaternion = new THREE.Quaternion();
    let up = new THREE.Vector3(0, 1, 0)
    if(base)
        up = up.applyAxisAngle(base, Math.PI);
    quaternion.setFromUnitVectors(up, direction);
    let euler = new THREE.Euler();
    euler.setFromQuaternion(quaternion); // Specify the order if needed
    parent.updateMatrixWorld();
    parent.rotation.set(euler.x, euler.y, euler.z);


    while(Math.abs(parent.rotation.y) > 0.01)
        parent.rotateY(-parent.rotation.y);


    parentparent.attach(parent);
    if(base)
        parent.rotateOnAxis(base, -Math.PI);
    parent.updateMatrixWorld();

}


function adjustRotationY(boneName, rotY) {
    let bone = skeleton.getObjectByName(boneName);

    bone.rotateY(rotY);
}

function updateSkeleton(keypoints) {
    if (!skeleton) return;
    //return;
    const global_positions = {  };
    

    for (const [boneName, keypointName] of Object.entries(boneNamesToKeypoints)) {
        const [x, y, z] = keypoints[keypoints_to_index[keypointName]];
        let adjustedPosition = new THREE.Vector3(x - 0.11, y + 0.19 , z + 2.22);
        global_positions[boneName] = adjustedPosition;
    }
    global_positions["mixamorigHips"] =  midPoint("mixamorigLeftUpLeg", "mixamorigRightUpLeg", global_positions, [1, 1]);
    global_positions["mixamorigHips"].add(new THREE.Vector3(0, 0.05, 0));
    global_positions["mixamorigSpine"] = midPoint("mixamorigNeck", "mixamorigHips", global_positions, [1, 3]);
    global_positions["mixamorigSpine1"] = midPoint("mixamorigNeck", "mixamorigHips", global_positions, [1, 1]);
    global_positions["mixamorigSpine2"] = midPoint("mixamorigNeck", "mixamorigHips", global_positions, [3, 1]);
    global_positions["mixamorigLeftShoulder"] = midPoint("mixamorigLeftArm", "mixamorigNeck", global_positions, [1, 1]);
    global_positions["mixamorigRightShoulder"] = midPoint("mixamorigRightArm", "mixamorigNeck", global_positions, [1, 1]);

    rotateParentBasedOnChild("mixamorigLeftArm", global_positions);
    rotateParentBasedOnChild("mixamorigRightArm", global_positions);
    
    
    rotateParentBasedOnChild("mixamorigLeftForeArm", global_positions);
    rotateParentBasedOnChild("mixamorigRightForeArm", global_positions);



    rotateParentBasedOnChild("mixamorigLeftUpLeg", global_positions, new THREE.Vector3(0, 0,    -1));  
    rotateParentBasedOnChild("mixamorigRightUpLeg", global_positions, new THREE.Vector3(0, 0, 1));

    
    rotateParentBasedOnChild("mixamorigLeftLeg", global_positions, new THREE.Vector3(0, 0, -1));
    //skeleton.getObjectByName("mixamorigLeftLeg").rotation.x = Math.PI; 
    rotateParentBasedOnChild("mixamorigRightLeg", global_positions, new THREE.Vector3(0, 0, 1));
    //skeleton.getObjectByName("mixamorigRightLeg").rotation.x = Math.PI; 

    for (const [boneName, position] of Object.entries(global_positions)) {
        let bone = skeleton.getObjectByName(boneName);
        //console.log(boneName, position);
        moveBoneToWorldPosition(bone, position);
    }


    normalizeLength("mixamorigRightUpLeg");
    normalizeLength("mixamorigLeftUpLeg");  
    //normalizeLength("mixamorigRightLeg");
    //normalizeLength("mixamorigLeftLeg");  

    //normalizeLength("mixamorigRightFoot");
    //normalizeLength("mixamorigLeftFoot");

    normalizeLength("mixamorigRightArm");
    normalizeLength("mixamorigLeftArm"); 
    normalizeLength("mixamorigRightForeArm");
    normalizeLength("mixamorigLeftForeArm"); 


    adjustRotationY("mixamorigRightLeg", Math.PI / 4);
    adjustRotationY("mixamorigLeftLeg",  Math.PI / 4);

}

