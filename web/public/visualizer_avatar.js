import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer, clock, controls;
let avatarBones = {};
let boneHierarchy = {};  // Auto-generated bone hierarchy
let keypointsData;
let frameIndex = 0;
let keypointsToIndex = {};

// Correct bone mapping for avatar rig
const bonesMapping = {
    "ROOT": "mixamorigHips_01",
    "SPINE": "mixamorigSpine_02",
    "NECK": "mixamorigNeck_03",
    
    "LEFT_SHOULDER": "mixamorigLeftShoulder_08",
    "LEFT_ARM": "mixamorigLeftArm_09",
    "LEFT_FOREARM": "mixamorigLeftForeArm_010",
    "LEFT_HAND": "mixamorigLeftHand_011",
    
    "RIGHT_SHOULDER": "mixamorigRightShoulder_012",
    "RIGHT_ARM": "mixamorigRightArm_013",
    "RIGHT_FOREARM": "mixamorigRightForeArm_014",
    "RIGHT_HAND": "mixamorigRightHand_015",
    
    "LEFT_UPLEG": "mixamorigLeftUpLeg_016",
    "LEFT_LEG": "mixamorigLeftLeg_017",
    "LEFT_FOOT": "mixamorigLeftFoot_018",
    
    "RIGHT_UPLEG": "mixamorigRightUpLeg_021",
    "RIGHT_LEG": "mixamorigRightLeg_022",
    "RIGHT_FOOT": "mixamorigRightFoot_023"
};

init();
loadAvatar();
fetchKeypoints();
animate();

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x202020);
    
    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.5, 3);
    
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 1;
    controls.maxDistance = 10;
    controls.maxPolarAngle = Math.PI / 2;

    clock = new THREE.Clock();

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(2, 2, 2);
    scene.add(light);

    window.addEventListener('resize', onWindowResize);
}

function loadAvatar() {
    const loader = new GLTFLoader();
    loader.load('stickman.glb', (gltf) => {
        const model = gltf.scene;
        scene.add(model);

        model.traverse((node) => {
            if (node.isBone) {
                avatarBones[node.name] = node;
                if (node.parent && node.parent.isBone) {
                    boneHierarchy[node.name] = node.parent.name; // Auto-extract parent-child relationship
                } else {
                    boneHierarchy[node.name] = null; // Root bone
                }
            }
        });

        console.log("Extracted Bone Hierarchy:", boneHierarchy);
    });
}

async function fetchKeypoints() {
    const response = await fetch('excercise.json');
    keypointsData = await response.json();

    // Extract the index mapping from JSON
    keypointsToIndex = keypointsData.body_keypoint_definitions.keypoints_to_index;
}

function animate() {
    requestAnimationFrame(animate);

    if (keypointsData && frameIndex in keypointsData.seq_data) {
        let keypoints = keypointsData.seq_data[frameIndex].keypoint;
        updateAvatarPose(keypoints);
        frameIndex = (frameIndex + 1) % Object.keys(keypointsData.seq_data).length;
    }

    controls.update();
    renderer.render(scene, camera);
}

function updateAvatarPose(keypoints) {
    //console.group('Frame Update');
    
    // Update root position first
    const rootBone = avatarBones[bonesMapping["ROOT"]];
    if (rootBone && keypoints[0]) {
        rootBone.position.set(
            keypoints[0][0],
            keypoints[0][1],
            keypoints[0][2]
        );
    }

    // Update other bones dynamically
    Object.entries(bonesMapping).forEach(([keypoint, boneName]) => {
        if (keypoint === "ROOT") return; // Skip root, already handled
        
        const bone = avatarBones[boneName];
        if (!bone) {
            //console.warn(`Missing bone: ${boneName}`);
            return;
        }

        const kpIndex = keypointsToIndex[keypoint];
        if (kpIndex === undefined || !keypoints[kpIndex]) {
            return;
        }

        //console.log(`Updating bone: ${boneName}, KeyPoint: ${keypoint}`);

        const position = new THREE.Vector3(
            keypoints[kpIndex][0],
            keypoints[kpIndex][1],
            keypoints[kpIndex][2]
        );

        // Get parent bone
        const parentBoneName = boneHierarchy[boneName];
        const parentBone = parentBoneName ? avatarBones[parentBoneName] : null;

        if (parentBone) {
            // Calculate rotation
            const localPos = position.clone().sub(parentBone.position);
            
            // Normalize the direction
            const boneDirection = localPos.normalize();
            
            // Apply rotation
            const quaternion = new THREE.Quaternion();
            quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), boneDirection);
            bone.quaternion.slerp(quaternion, 0.5);
        }
    });

    //console.groupEnd();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}