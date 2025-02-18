import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class BodyTrackingVisualizer {
    constructor(container, trackedData) {
        this.trackedData = trackedData;
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        // Camera position (adjusted for your coordinate system)
        this.camera.position.set(0, 0, 0);
        
        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        // Points and lines
        this.joints = new Map();
        this.bones = [];
        this.currentFrame = 0;
        this.container = container;

        // Setup
        this.setupScene();
        this.setupLights();
        this.createVisualization();

        // Animation
        this.animate = this.animate.bind(this);
        this.animate();
    }

    setupScene() {
        // Add grid for reference
        //const gridHelper = new THREE.GridHelper(5, 10);
        //gridHelper.rotation.x = Math.PI / 2; // Rotate grid to match coordinate system
        //this.scene.add(gridHelper);

        // Add axes helper
        //const axesHelper = new THREE.AxesHelper(1);
        //this.scene.add(axesHelper);
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
    }

    createVisualization() {
        // Materials
        this.jointMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        this.lowConfidenceJointMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
        this.boneMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
        const jointGeometry = new THREE.SphereGeometry(0.02);

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
            // Handle special case for spine connections
            let fromKey = from;
            if (fromKey === "spine") {
                fromKey = "NECK";
            }
            const fromIndex = keyPointsToIndex[fromKey];
            const toIndex = keyPointsToIndex[to];
            
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

    updateFrame(frameIndex) {
        const frame = this.trackedData.seq_data[frameIndex.toString()];
        if (!frame) return;

        // Update joints
        frame.keypoint.forEach((position, index) => {
            const joint = this.joints.get(index);
            if (joint) {
                joint.position.set(position[0], position[1], position[2]);
                joint.material = frame.keypoint_confidence[index] > 50 ? 
                    this.jointMaterial : this.lowConfidenceJointMaterial;
            }
        });

        // Update bones
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
    }

    animate() {
        requestAnimationFrame(this.animate);
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
        
        // Handle window resize
        window.addEventListener('resize', () => visualizer.onWindowResize(), false);
        
        // Animate through frames
        let currentFrame = 0;
        const totalFrames = Object.keys(trackedData.seq_data).length;
        
        // Use requestAnimationFrame for smoother animation
        function animateFrames() {
            visualizer.updateFrame(currentFrame);
            currentFrame = (currentFrame + 1) % totalFrames;
            // Schedule next frame based on video FPS
            setTimeout(() => {
                requestAnimationFrame(animateFrames);
            }, 1000 / trackedData.camera_fps);
        }
        
        // Start the frame animation
        animateFrames();
        
    } catch (error) {
        console.error('Error initializing visualizer:', error);
    }
}

// Initialize the visualization
initializeVisualizer();