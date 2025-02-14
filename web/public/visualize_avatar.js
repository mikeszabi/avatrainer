import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CCDIKSolver } from 'three/addons/animation/CCDIKSolver.js';

async function fetchKeypoints() {
    try {
        const response = await fetch('excercise.json');
        const data = await response.json();

        // Validate data before returning
        if (!data || !data.seq_data || !data.body_keypoint_definitions) {
            throw new Error('Invalid sequence data provided');
        }

        return data;
    } catch (error) {
        console.error("Error fetching sequence data:", error);
        return null;
    }
}

class AvatarAnimator {
    constructor(sequenceData) {
        if (!sequenceData) {
            throw new Error('No valid sequence data provided');
        }
        this.sequenceData = sequenceData;
        this.currentFrame = 0;
        this.isAnimating = false;

        // Setup scene
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);

        // Setup camera and controls
        this.camera.position.z = 5;
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 1, 1);
        this.scene.add(ambientLight, directionalLight);

        // Store bones and IK targets
        this.bones = {};
        this.ikTargets = {};
        this.keypointMapping = {
            'NOSE': 'mixamorigHead_06',
            'NECK': 'mixamorigNeck_05',
            'LEFT_SHOULDER': 'mixamorigLeftShoulder_08',
            'RIGHT_SHOULDER': 'mixamorigRightShoulder_012',
            'LEFT_ELBOW': 'mixamorigLeftForeArm_010',
            'RIGHT_ELBOW': 'mixamorigRightForeArm_014',
            'LEFT_WRIST': 'mixamorigLeftHand_011',
            'RIGHT_WRIST': 'mixamorigRightHand_015',
            'LEFT_HIP': 'mixamorigLeftUpLeg_016',
            'RIGHT_HIP': 'mixamorigRightUpLeg_021',
            'LEFT_KNEE': 'mixamorigLeftLeg_017',
            'RIGHT_KNEE': 'mixamorigRightLeg_022',
            'LEFT_ANKLE': 'mixamorigLeftFoot_018',
            'RIGHT_ANKLE': 'mixamorigRightFoot_023',
            'spine': 'mixamorigSpine_02'
        };

        this.loadAvatar();
    }

    async loadAvatar() {
        const loader = new GLTFLoader();
        try {
            const gltf = await loader.loadAsync('stickman.glb');
            this.avatar = gltf.scene;
            this.scene.add(this.avatar);
    
            // Ensure bones are properly stored
            this.bones = {}; // Reset bones object
            this.avatar.traverse((node) => {
                if (node.isBone) {
                    this.bones[node.name] = node;
                }
            });
    
            console.log("Loaded avatar bones:", Object.keys(this.bones)); // Debugging
    
            // Verify that bones are actually loaded before proceeding
            if (Object.keys(this.bones).length === 0) {
                throw new Error("No bones were found in the avatar model.");
            }
    
            // Setup IK chains only if bones exist
            this.setupIKChains();
    
            // Start animation loop
            this.animate();
    
            // Start the animation sequence if valid data exists
            if (this.sequenceData && this.sequenceData.seq_data) {
                this.startAnimation();
            }
        } catch (error) {
            console.error('Error loading avatar:', error);
        }
    }
    

    setupIKChains() {
        if (!this.bones || Object.keys(this.bones).length === 0) {
            console.error("Cannot setup IK chains: No bones found.");
            return;
        }
    
        // Debug bone hierarchy before setup
        console.group('Initial Bone Hierarchy');
        Object.entries(this.bones).forEach(([name, bone]) => {
            console.log(`Bone: ${name}`);
            console.log(`- Parent: ${bone.parent?.name || 'none'}`);
            console.log(`- Children: ${bone.children.map(c => c.name).join(', ')}`);
        });
        console.groupEnd();
    
        const chains = [
            {
                name: 'leftArm',
                target: 'LEFT_WRIST',
                joints: ['mixamorigSpine_02', 'mixamorigLeftShoulder_08', 'mixamorigLeftArm_09', 'mixamorigLeftForeArm_010']
            },
            {
                name: 'rightArm',
                target: 'RIGHT_WRIST',
                joints: ['mixamorigSpine_02', 'mixamorigRightShoulder_012', 'mixamorigRightArm_013', 'mixamorigRightForeArm_014']
            }
        ];
    
        // Validate and create IK chains
        const validChains = chains.map(chain => {
            console.group(`Validating chain: ${chain.name}`);
            
            // Get bones and verify existence
            const bones = chain.joints.map(name => {
                const bone = this.bones[name];
                if (!bone) {
                    console.warn(`Missing bone: ${name}`);
                    return null;
                }
                return bone;
            }).filter(Boolean);
    
            if (bones.length !== chain.joints.length) {
                console.error(`Invalid chain ${chain.name}: missing bones`);
                console.groupEnd();
                return null;
            }
    
            // Verify parent-child relationships
            for (let i = 1; i < bones.length; i++) {
                let current = bones[i];
                let parent = bones[i - 1];
                
                // Check direct parent or ancestor
                let hasValidParent = false;
                let checkNode = current.parent;
                while (checkNode) {
                    if (checkNode === parent) {
                        hasValidParent = true;
                        break;
                    }
                    checkNode = checkNode.parent;
                }
    
                if (!hasValidParent) {
                    console.error(`Invalid hierarchy: ${current.name} is not a descendant of ${parent.name}`);
                    console.groupEnd();
                    return null;
                }
            }
    
            console.log('Valid chain:', bones.map(b => b.name));
            console.groupEnd();
            
            // Create target
            const target = new THREE.Object3D();
            this.scene.add(target);
            this.ikTargets[chain.target] = target;
    
            return {
                target: target,
                effector: bones[bones.length - 1],
                links: bones.slice(1).map(bone => ({
                    enabled: true,
                    joint: bone
                }))
            };
        }).filter(Boolean);
    
        if (validChains.length > 0) {
            try {
                let skinnedMesh;
                this.avatar.traverse((node) => {
                    if (node.isSkinnedMesh) {
                        skinnedMesh = node;
                        console.log('Found skinned mesh:', node.name);
                    }
                });
    
                if (!skinnedMesh) throw new Error('No skinned mesh found');

                console.log('valid_chain:',validChains)
                
                this.ikSolver = new CCDIKSolver(skinnedMesh, validChains);
                console.log('IK solver created successfully');
            } catch (error) {
                console.error('Failed to create IK solver:', error);
                console.error('Error details:', error.stack);
            }
        }
    }
    

    updatePose(keypoints, keypointDefinitions) {
        if (!keypoints || !keypointDefinitions) {
            console.warn('Invalid keypoints or definitions');
            return;
        }

        const worldKeypoints = {};
        Object.entries(keypointDefinitions.keypoints_to_index).forEach(([name, index]) => {
            if (keypoints[index] && Array.isArray(keypoints[index]) && keypoints[index].length === 3) {
                worldKeypoints[name] = new THREE.Vector3(...keypoints[index]);
            }
        });

        Object.entries(this.keypointMapping).forEach(([keypoint, boneName]) => {
            if (worldKeypoints[keypoint] && this.ikTargets[keypoint]) {
                this.ikTargets[keypoint].position.copy(worldKeypoints[keypoint]);
            }
        });

        if (this.ikSolver) {
            this.ikSolver.update();
        }
    }

    startAnimation() {
        this.isAnimating = true;
        this.currentFrame = 0;
        this.animate();
    }

    animate() {
        if (!this.isAnimating) return;
        requestAnimationFrame(() => this.animate());

        const frameKeys = Object.keys(this.sequenceData.seq_data);
        if (frameKeys.length > 0) {
            const frameData = this.sequenceData.seq_data[frameKeys[this.currentFrame]];
            if (frameData) {
                this.updatePose(frameData.keypoint, this.sequenceData.body_keypoint_definitions);
            }
            this.currentFrame = (this.currentFrame + 1) % frameKeys.length;
        }

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

fetchKeypoints().then(data => {
    if (data) {
        new AvatarAnimator(data);
    }
});
