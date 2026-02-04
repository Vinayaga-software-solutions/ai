document.addEventListener('DOMContentLoaded', () => {
    // Reveal animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Once visible, no need to observe anymore
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const revealElements = document.querySelectorAll('.reveal');
    revealElements.forEach(el => observer.observe(el));

    // Smooth momentum scroll effect (simulated)
    // We'll use a simpler version: smooth scroll for anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile nav toggle
    const navShell = document.querySelector('.nav-shell');
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navShell && navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            const isOpen = navShell.classList.toggle('nav-open');
            navToggle.setAttribute('aria-expanded', String(isOpen));
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navShell.classList.remove('nav-open');
                navToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // Parallax effect for hero image
    const heroImage = document.querySelector('.hero-image img');
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        if (heroImage) {
            heroImage.style.transform = `rotateX(${10 - scrolled * 0.02}deg) translateY(${scrolled * 0.1}px)`;
        }
    });

    // Add staggered delay to reveal elements in groups
    const gridReveals = document.querySelectorAll('.grid .reveal');
    gridReveals.forEach((el, index) => {
        el.style.transitionDelay = `${index * 0.15}s`;
    });
});
