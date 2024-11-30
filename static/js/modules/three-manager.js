import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

class ThreeManager {
    constructor() {
        if (ThreeManager.instance) {
            return ThreeManager.instance;
        }
        ThreeManager.instance = this;
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.torus = null;
    }

    initialize() {
        // إنشاء المشهد
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true,
            antialias: true 
        });
        
        // تهيئة العرض
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(this.renderer.domElement);
        
        // إنشاء الشكل
        const geometry = new THREE.TorusGeometry(10, 3, 16, 100);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0x6366f1, 
            wireframe: true,
            transparent: true,
            opacity: 0.5
        });
        this.torus = new THREE.Mesh(geometry, material);
        
        this.scene.add(this.torus);
        this.camera.position.z = 30;
        
        // تحديث الحجم عند تغيير حجم النافذة
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
        
        this.animate();
    }

    onWindowResize() {
        if (this.camera && this.renderer) {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        }
    }

    animate() {
        if (this.torus && this.renderer && this.scene && this.camera) {
            requestAnimationFrame(this.animate.bind(this));
            this.torus.rotation.x += 0.01;
            this.torus.rotation.y += 0.01;
            this.renderer.render(this.scene, this.camera);
        }
    }

    cleanup() {
        if (this.renderer) {
            this.renderer.dispose();
            document.body.removeChild(this.renderer.domElement);
        }
    }
}

// تصدير نسخة واحدة
export const threeManager = new ThreeManager(); 