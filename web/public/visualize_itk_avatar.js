import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CCDIKSolver } from 'three/addons/animation/CCDIKSolver.js';

// Scene setup
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
let renderer = new THREE.WebGLRenderer({ antialias: true });
let clock = new THREE.Clock();
let controls;

// Avatar state
let avatarBones = {};
let ikSolver = null;
let ikTargets = new Map();
let keypointsData;
let frameIndex = 0;

// Initialize scene
function init() {
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    
    camera.position.set(0, 1.6, 3);
    controls = new OrbitControls(camera, renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 10, 10);
    scene.add(ambientLight, directionalLight);
}

// IK Chain definitions
const ikChainDefs = [
    {
        name: 'leftArm',
        target: 'LEFT_HAND',
        effector: 'mixamorigLeftHand_011',
        joints: ['mixamorigLeftShoulder_08', 'mixamorigLeftArm_09', 'mixamorigLeftForeArm_010']
    },
    {
        name: 'rightArm',
        target: 'RIGHT_HAND',
        effector: 'mixamorigRightHand_015',
        joints: ['mixamorigRightShoulder_012', 'mixamorigRightArm_013', 'mixamorigRightForeArm_014']
    }
];

function loadAvatar() {
    const loader = new GLTFLoader();
    loader.load('stickman.glb', (gltf) => {
        scene.add(gltf.scene);
        
        gltf.scene.traverse((node) => {
            if (node.isBone) {
                avatarBones[node.name] = node;
                console.log(`Loaded bone: ${node.name}`);
            }
        });
        
        setupIKSolver();
    });
}

function setupIKSolver() {
    // Create IK chains
    const iks = ikChainDefs.map(chain => {
        // Create target
        const target = new THREE.Object3D();
        scene.add(target);
        ikTargets.set(chain.name, target);
        
        // Verify bones exist
        const effector = avatarBones[chain.effector];
        const joints = chain.joints.map(name => avatarBones[name]).filter(Boolean);
        
        if (!effector || joints.length !== chain.joints.length) {
            console.warn(`Missing bones for chain ${chain.name}`);
            return null;
        }
        
        return {
            target: target,
            effector: effector,
            links: joints.map(joint => ({
                enabled: true,
                joint: joint
            }))
        };
    }).filter(Boolean);
    
    if (iks.length > 0) {
        ikSolver = new CCDIKSolver(scene, iks);
    }
}

function updateIKTargets(keypoints) {
    if (!ikSolver) return;
    
    ikChainDefs.forEach(chain => {
        const target = ikTargets.get(chain.name);
        const kpIndex = keypointsData.body_keypoint_definitions.keypoints_to_index[chain.target];
        
        if (target && keypoints[kpIndex]) {
            target.position.set(
                keypoints[kpIndex][0],
                keypoints[kpIndex][1],
                keypoints[kpIndex][2]
            );
        }
    });
    
    ikSolver.update();
}

function animate() {
    requestAnimationFrame(animate);
    
    if (keypointsData && frameIndex in keypointsData.seq_data) {
        const keypoints = keypointsData.seq_data[frameIndex].keypoint;
        updateIKTargets(keypoints);
        frameIndex = (frameIndex + 1) % Object.keys(keypointsData.seq_data).length;
    }
    
    controls.update();
    renderer.render(scene, camera);
}

// Initialize and start
init();
loadAvatar();
animate();