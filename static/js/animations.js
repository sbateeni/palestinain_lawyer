export function initAnimations() {
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