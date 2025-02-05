import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

class BodyTrackingVisualizer {
    constructor(container, trackedData) {
        this.trackedData = trackedData;
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        // Camera position
        this.camera.position.set(0, 1, 3);
        
        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        // Storage
        this.joints = new Map();
        this.bones = [];
        this.currentFrame = 0;
        this.container = container;
        this.avatar = null;
        this.avatarBones = new Map();
        this.avatarSkinnedMesh = null;
        this.mixer = null;  // Animation mixer
        this.clock = new THREE.Clock(); // Used for animation updates

        // Setup
        this.setupScene();
        this.createVisualization();
        this.loadAvatar();

        // Animation
        this.animate = this.animate.bind(this);
        this.animate();
    }

    setupScene() {
        const gridHelper = new THREE.GridHelper(5, 10);
        this.scene.add(gridHelper);

        // Lighting setup
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
    }

    async loadAvatar() {
        const loader = new GLTFLoader();
        
        try {
            const gltf = await new Promise((resolve, reject) => {
                loader.load(
                    './avatar/scene.gltf',
                    resolve,
                    undefined,
                    reject
                );
            });

            this.avatar = gltf.scene;
            this.scene.add(this.avatar);

            console.log('GLTF Model Loaded:', gltf);
            console.log('Animations:', gltf.animations);

            // Find the SkinnedMesh
            let skinnedMeshFound = false;
            this.avatar.traverse((node) => {
                console.log(`Node Name: ${node.name}, Type: ${node.type}`);
                if (node.type === 'SkinnedMesh') {
                    this.avatarSkinnedMesh = node;
                    skinnedMeshFound = true;
                }
            });

            if (!skinnedMeshFound) {
                console.error('❌ No SkinnedMesh found in the avatar. Ensure the model is rigged properly.');
                return;
            }

            // Initialize pose mapping
            this.initializeAvatarPose();

            // If animations exist, initialize animation mixer
            // if (gltf.animations.length > 0) {
            //     this.mixer = new THREE.AnimationMixer(this.avatar);
            //     this.animationAction = this.mixer.clipAction(gltf.animations[0]); // Play first animation
            //     this.animationAction.play();
            //     console.log('✅ Animation started');
            // } else {
            //     console.warn('⚠ No animations found in the GLTF file.');
            // }

        } catch (error) {
            console.error('Error loading avatar:', error);
        }
    }

    initializeAvatarPose() {
        if (!this.avatarSkinnedMesh) return;

        const skeleton = this.avatarSkinnedMesh.skeleton;
        
        // Map bones to keypoints

        //"body_model": "BODY_18", "body_keypoint_definitions": {"keypoints_to_index": {"NOSE": 0, "LEFT_HIP": 11, "RIGHT_HIP": 8, "LEFT_KNEE": 12, "RIGHT_KNEE": 9, "LEFT_ANKLE": 13, "RIGHT_ANKLE": 10, "LEFT_SHOULDER": 5, "RIGHT_SHOULDER": 2, "LEFT_ELBOW": 6, "RIGHT_ELBOW": 3, "LEFT_WRIST": 7, "RIGHT_WRIST": 4, "NECK": 1}
        
        const boneMapping = {
            'Hips': 8,        
            'Spine': 1,       
            'Head': 0,        
            'LeftUpLeg': 11,  
            'LeftLeg': 12,    
            'LeftFoot': 13,   
            'RightUpLeg': 8,  
            'RightLeg': 9,    
            'RightFoot': 10,  
            'LeftShoulder': 5,
            'LeftArm': 6,     
            'LeftForeArm': 7, 
            'RightShoulder': 2, 
            'RightArm': 3,    
            'RightForeArm': 4 
        };

        // Map bones and store initial rotations
        skeleton.bones.forEach(bone => {
            const keypointIndex = boneMapping[bone.name];
            if (keypointIndex !== undefined) {
                this.avatarBones.set(keypointIndex, {
                    bone: bone,
                    initialRotation: bone.rotation.clone(),
                    initialPosition: bone.position.clone()
                });
            }
        });
    }

    createVisualization() {
        // Materials
        this.jointMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        this.lowConfidenceJointMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
        this.boneMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
        const jointGeometry = new THREE.SphereGeometry(0.02);
    
        // Check if tracking data exists
        if (!this.trackedData || !this.trackedData.seq_data["0"]) {
            console.error("❌ Tracking data is missing or corrupted.");
            return;
        }
    
        // Create joints
        const firstFrame = this.trackedData.seq_data["0"];
        firstFrame.keypoint.forEach((position, index) => {
            const joint = new THREE.Mesh(jointGeometry, 
                firstFrame.keypoint_confidence[index] > 50 ? this.jointMaterial : this.lowConfidenceJointMaterial);
            joint.position.set(position[0], position[1], position[2]);
            this.scene.add(joint);
            this.joints.set(index, joint);
        });
    
        // Create bones based on connections
        const connections = this.trackedData.body_keypoint_definitions.connections;
        const keyPointsToIndex = this.trackedData.body_keypoint_definitions.keypoints_to_index;
        
        connections.forEach(([from, to]) => {
            let fromIndex = keyPointsToIndex[from];
            let toIndex = keyPointsToIndex[to];
            
            if (fromIndex !== undefined && toIndex !== undefined) {
                const geometry = new THREE.BufferGeometry();
                const fromJoint = this.joints.get(fromIndex);
                const toJoint = this.joints.get(toIndex);
                
                if (fromJoint && toJoint) {
                    const vertices = new Float32Array([
                        fromJoint.position.x, fromJoint.position.y, fromJoint.position.z,
                        toJoint.position.x, toJoint.position.y, toJoint.position.z
                    ]);
                    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
                    const line = new THREE.Line(geometry, this.boneMaterial);
                    this.bones.push({ line, fromIndex, toIndex });
                    this.scene.add(line);
                }
            }
        });
    }
    

    findConnectedKeypoint(keypointIndex, frame) {
        const connections = this.trackedData.body_keypoint_definitions.connections;
        const keyPointsToIndex = this.trackedData.body_keypoint_definitions.keypoints_to_index;

        for (const [from, to] of connections) {
            if (keyPointsToIndex[from] === keypointIndex) {
                return new THREE.Vector3(...frame.keypoint[keyPointsToIndex[to]]);
            } else if (keyPointsToIndex[to] === keypointIndex) {
                return new THREE.Vector3(...frame.keypoint[keyPointsToIndex[from]]);
            }
        }
        return null;
    }

    updateAvatarPose(frame) {
        if (!this.avatarSkinnedMesh || !frame) return;
    
        // Get root position (Hips - Keypoint 8)
        const rootPos = frame.keypoint[8];
        if (rootPos) {
            this.avatar.position.set(rootPos[0], rootPos[1], rootPos[2]);
        }
    
        // Adjust scale if needed
        this.avatar.scale.set(0.4, 0.4, 0.4); // Adjust if avatar is too big/small
        this.avatar.rotation.set(0, -Math.PI/2, 0); // Flip 180 degrees if needed
        this.avatar.position.y -= 0.75; // Adjust height
    
        // Iterate through all mapped bones
        this.avatarBones.forEach((boneData, keypointIndex) => {
            const { bone, initialRotation } = boneData;
            const currentPos = frame.keypoint[keypointIndex];
            
            if (!currentPos) return;
    
            // Find the connected keypoint
            const connectedPos = this.findConnectedKeypoint(keypointIndex, frame);
            if (!connectedPos) return;
    
            // Convert to Three.js vectors
            const start = new THREE.Vector3(currentPos[0], currentPos[1], currentPos[2]);
            const end = new THREE.Vector3(connectedPos[0], connectedPos[1], connectedPos[2]);
            const direction = end.sub(start).normalize();
    
            // Adjust rotation to align bones properly
            const boneDirection = new THREE.Vector3(0, 1, 0); // Default bone direction
            const quaternion = new THREE.Quaternion();
            quaternion.setFromUnitVectors(boneDirection, direction);
    
            // Apply rotation
            bone.quaternion.copy(initialRotation.clone().multiply(quaternion));
            bone.updateMatrix();
        });
    
        // Update skeleton
        this.avatarSkinnedMesh.skeleton.update();
    }

    updateFrame(frameIndex) {
        const frame = this.trackedData.seq_data[frameIndex.toString()];
        if (!frame) return;

        // Update joints visualization
        frame.keypoint.forEach((position, index) => {
            const joint = this.joints.get(index);
            if (joint) {
                joint.position.set(position[0], position[1], position[2]);
            }
        });

        // Update bones visualization
        this.bones.forEach(({ line, fromIndex, toIndex }) => {
            const positions = line.geometry.attributes.position.array;
            const fromPos = frame.keypoint[fromIndex];
            const toPos = frame.keypoint[toIndex];
            
            positions[0] = fromPos[0];
            positions[1] = fromPos[1];
            positions[2] = fromPos[2];
            positions[3] = toPos[0];
            positions[4] = toPos[1];
            positions[5] = toPos[2];

            line.geometry.attributes.position.needsUpdate = true;
        });

        // Update avatar pose
        this.updateAvatarPose(frame);
    }

    animate() {
        requestAnimationFrame(this.animate);
        
        const delta = this.clock.getDelta();
        if (this.mixer) {
            this.mixer.update(delta);
        }

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
}

async function initializeVisualizer() {
    try {
        const response = await fetch('excercise.json');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const trackedData = await response.json();
        
        const container = document.getElementById('container');
        const visualizer = new BodyTrackingVisualizer(container, trackedData);
        
        window.addEventListener('resize', () => visualizer.onWindowResize(), false);
        
        let currentFrame = 0;
        const totalFrames = Object.keys(trackedData.seq_data).length;
        
        function animateFrames() {
            visualizer.updateFrame(currentFrame);
            currentFrame = (currentFrame + 1) % totalFrames;
            setTimeout(() => {
                requestAnimationFrame(animateFrames);
            }, 1000 / trackedData.camera_fps);
        }
        
        animateFrames();
        
    } catch (error) {
        console.error('Error initializing visualizer:', error);
    }
}

initializeVisualizer();