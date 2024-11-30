class UIManager {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // تهيئة مستمعي الأحداث للواجهة
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeAnimations();
            this.initializeScrollEffects();
        });
    }

    initializeAnimations() {
        // تطبيق التأثيرات الحركية على العناصر
        gsap.from('.hero-section', {
            duration: 1,
            y: 50,
            opacity: 0,
            ease: 'power3.out'
        });

        gsap.from('.stage-card', {
            duration: 0.8,
            y: 30,
            opacity: 0,
            stagger: 0.2,
            ease: 'back.out'
        });
    }

    initializeScrollEffects() {
        // تطبيق تأثيرات التمرير
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('show');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

export const uiManager = new UIManager(); 