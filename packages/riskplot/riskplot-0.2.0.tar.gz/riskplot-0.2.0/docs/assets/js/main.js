// RiskPlot Documentation JavaScript

// Gallery data with all visualizations
const galleryData = [
    {
        id: 'ridge-portfolios',
        title: 'Portfolio Return Distributions',
        description: 'Compare return distributions across different asset classes and portfolios.',
        image: 'assets/images/ridge_plot_portfolios.png',
        category: 'distributions',
        tags: ['ridge-plots', 'distributions', 'portfolios']
    },
    {
        id: 'ridge-sectors',
        title: 'Sector Performance Analysis',
        description: 'Analyze performance distributions across market sectors.',
        image: 'assets/images/ridge_plot_sectors.png',
        category: 'distributions',
        tags: ['ridge-plots', 'sectors', 'performance']
    },
    {
        id: 'heatmap-correlation',
        title: 'Asset Correlation Matrix',
        description: 'Visualize correlations between different asset classes.',
        image: 'assets/images/heatmap_correlations.png',
        category: 'risk',
        tags: ['heatmaps', 'correlation', 'assets']
    },
    {
        id: 'heatmap-factors',
        title: 'Risk Factor Exposure',
        description: 'Map portfolio exposures to various risk factors.',
        image: 'assets/images/heatmap_risk_factors.png',
        category: 'risk',
        tags: ['heatmaps', 'risk-factors', 'exposure']
    },
    {
        id: 'heatmap-country',
        title: 'Country Risk Assessment',
        description: 'Geographic risk assessment across multiple countries.',
        image: 'assets/images/heatmap_country_risk.png',
        category: 'risk',
        tags: ['heatmaps', 'country-risk', 'geographic']
    },
    {
        id: 'waterfall-attribution',
        title: 'Return Attribution Analysis',
        description: 'Break down portfolio returns by contributing factors.',
        image: 'assets/images/waterfall_attribution.png',
        category: 'risk',
        tags: ['waterfall', 'attribution', 'factors']
    },
    {
        id: 'waterfall-risk-budget',
        title: 'Risk Budget Decomposition',
        description: 'Decompose total portfolio risk by source.',
        image: 'assets/images/waterfall_risk_budget.png',
        category: 'risk',
        tags: ['waterfall', 'risk-budget', 'var']
    },
    {
        id: 'timeseries-var',
        title: 'VaR Time Series Monitoring',
        description: 'Track Value at Risk over time with rolling metrics.',
        image: 'assets/images/timeseries_example.png',
        category: 'timeseries',
        tags: ['timeseries', 'var', 'monitoring']
    },
    {
        id: 'drawdown-analysis',
        title: 'Portfolio Drawdown Analysis',
        description: 'Analyze portfolio drawdowns and recovery periods.',
        image: 'assets/images/drawdown_example.png',
        category: 'timeseries',
        tags: ['drawdown', 'performance', 'risk']
    },
    {
        id: 'risk-matrix',
        title: 'Risk Assessment Matrix',
        description: 'Probability vs impact analysis for risk events.',
        image: 'assets/images/risk_matrix_example.png',
        category: 'risk',
        tags: ['risk-matrix', 'probability', 'impact']
    },
    {
        id: 'country-risk-bar',
        title: 'Country Risk Scoring',
        description: 'Country-level risk scores with color-coded indicators.',
        image: 'assets/images/country_risk_example.png',
        category: 'risk',
        tags: ['country-risk', 'geographic', 'scoring']
    }
];

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeGallery();
    initializeScrollEffects();
    initializeCopyButtons();
    initializeSmoothScrolling();
});

// Navigation functionality
function initializeNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Mobile menu toggle
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking on links
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
            }
        });
    }

    // Active navigation highlighting
    const sections = document.querySelectorAll('section[id]');
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const activeLink = document.querySelector(`[href="#${entry.target.id}"]`);
                    navLinks.forEach(link => link.classList.remove('active'));
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        },
        { threshold: 0.3 }
    );

    sections.forEach(section => observer.observe(section));
}

// Gallery functionality
function initializeGallery() {
    const galleryGrid = document.getElementById('galleryGrid');
    const filterButtons = document.querySelectorAll('.filter-btn');

    if (!galleryGrid) return;

    // Render gallery items
    function renderGallery(items = galleryData) {
        galleryGrid.innerHTML = items.map(item => `
            <div class="gallery-item" data-category="${item.category}">
                <img src="${item.image}" alt="${item.title}" loading="lazy">
                <div class="gallery-item-content">
                    <div class="gallery-item-tag">${item.category}</div>
                    <h3>${item.title}</h3>
                    <p>${item.description}</p>
                </div>
            </div>
        `).join('');

        // Add fade-in animation to new items
        const items_elements = galleryGrid.querySelectorAll('.gallery-item');
        items_elements.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            setTimeout(() => {
                item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');

            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Filter gallery items
            const filteredItems = filter === 'all'
                ? galleryData
                : galleryData.filter(item => item.category === filter);

            renderGallery(filteredItems);
        });
    });

    // Initial render
    renderGallery();
}

// Scroll effects
function initializeScrollEffects() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }

        lastScrollTop = scrollTop;
    });

    // Fade-in animation for elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe elements for fade-in animation
    const fadeElements = document.querySelectorAll('.feature-card, .step, .footer-section');
    fadeElements.forEach(el => {
        el.classList.add('fade-in');
        fadeObserver.observe(el);
    });
}

// Copy to clipboard functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');

    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.previousElementSibling.textContent ||
                              this.getAttribute('data-text');

            copyToClipboard(textToCopy);

            // Visual feedback
            const originalIcon = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                this.innerHTML = originalIcon;
            }, 1500);
        });
    });
}

// Copy to clipboard utility function
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        // Modern approach
        return navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(text);
    }
}

// Fallback copy function
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        showToast('Copy failed. Please copy manually.');
    }

    document.body.removeChild(textArea);
}

// Toast notification
function showToast(message, duration = 3000) {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create new toast
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--gray-900);
        color: var(--white);
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        z-index: 10000;
        opacity: 0;
        transform: translateY(100%);
        transition: all 0.3s ease;
        font-weight: 500;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 100);

    // Animate out and remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Utility functions
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Performance optimization for scroll events
const debouncedScrollHandler = debounce(function() {
    // Any heavy scroll operations can go here
}, 10);

window.addEventListener('scroll', debouncedScrollHandler);

// Preload images for better performance
function preloadImages() {
    galleryData.forEach(item => {
        const img = new Image();
        img.src = item.image;
    });
}

// Initialize image preloading after page load
window.addEventListener('load', preloadImages);

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.style.display = 'none';
        console.warn('Failed to load image:', e.target.src);
    }
}, true);

// Export functions for potential use in other scripts
window.RiskPlotDocs = {
    copyToClipboard,
    showToast,
    galleryData
};