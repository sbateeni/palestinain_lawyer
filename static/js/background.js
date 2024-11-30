import { threeManager } from './modules/three-manager.js';

export function initBackground() {
    try {
        threeManager.initialize();
    } catch (error) {
        console.error('Error initializing background:', error);
    }
}

// تنظيف عند مغادرة الصفحة
window.addEventListener('beforeunload', () => {
    threeManager.cleanup();
});














