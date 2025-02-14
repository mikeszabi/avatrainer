import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import Stats from 'three/addons/libs/stats.module.js';

class AvatarDisplay {
    constructor() {
        this.debug = {
            enabled: true,
            showWireframe: false,
            showBones: false,
            showStats: true
        };
        
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.clock = new THREE.Clock();
        this.mixer = null;
        this.avatar = null;
        
        this.init();
    }

    init() {
        // Renderer setup
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);

        // Camera setup
        this.camera.position.set(0, 1.6, 3);
        
        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        
        // Debug setup
        if (this.debug.enabled) {
            this.setupDebug();
        }

        this.setupLights();
        this.loadAvatar();
        this.animate();
    }

    setupDebug() {
        // Stats
        if (this.debug.showStats) {
            this.stats = new Stats();
            document.body.appendChild(this.stats.dom);
        }

        // Debug UI
        const debugUI = document.createElement('div');
        debugUI.id = 'debug-panel';
        debugUI.style.cssText = `
            position: fixed;
            top: 0;
            right: 0;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            font-family: monospace;
        `;
        document.body.appendChild(debugUI);

        // Debug controls
        const controls = {
            wireframe: () => {
                if (this.avatar) {
                    this.avatar.traverse(node => {
                        if (node.isMesh) {
                            node.material.wireframe = this.debug.showWireframe;
                        }
                    });
                }
            },
            bones: () => {
                if (this.avatar && this.debug.showBones) {
                    const helper = new THREE.SkeletonHelper(this.avatar);
                    this.scene.add(helper);
                }
            }
        };

        // Add debug buttons
        Object.entries(controls).forEach(([name, func]) => {
            const button = document.createElement('button');
            button.textContent = `Toggle ${name}`;
            button.onclick = () => {
                this.debug[`show${name.charAt(0).toUpperCase() + name.slice(1)}`] = 
                    !this.debug[`show${name.charAt(0).toUpperCase() + name.slice(1)}`];
                func();
            };
            debugUI.appendChild(button);
        });
    }

    loadAvatar() {
        const loader = new GLTFLoader();
        loader.load(
            'stickman.glb',
            (gltf) => {
                console.group('Avatar Load Info');
                this.avatar = gltf.scene;
                
                // Log model structure
                this.avatar.traverse(node => {
                    console.log(`Node: ${node.name}, Type: ${node.type}`);
                    if (node.isBone) console.log(`Bone: ${node.name}`);
                    if (node.isMesh) console.log(`Mesh: ${node.name}`);
                });
                
                this.scene.add(this.avatar);

                // Setup animations
                if (gltf.animations.length) {
                    this.mixer = new THREE.AnimationMixer(this.avatar);
                    const action = this.mixer.clipAction(gltf.animations[0]);
                    action.play();
                }
                
                console.groupEnd();
            },
            (xhr) => {
                const progress = (xhr.loaded / xhr.total * 100).toFixed(2);
                console.log(`Loading: ${progress}%`);
            },
            (error) => console.error('Loading Error:', error)
        );
    }

    animate() {
        requestAnimationFrame(this.animate.bind(this));

        if (this.mixer) {
            this.mixer.update(this.clock.getDelta());
        }

        if (this.debug.enabled && this.debug.showStats) {
            this.stats.update();
        }

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    setupLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.1);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.1);
        directionalLight.position.set(5,5,5);
        this.scene.add(ambientLight, directionalLight);
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

// Initialize
const avatarDisplay = new AvatarDisplay();
window.addEventListener('resize', () => avatarDisplay.onWindowResize());