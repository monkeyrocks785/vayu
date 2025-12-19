<<<<<<< HEAD
// Enhanced JavaScript for VAYU Weather App
// Adds smooth interactions, animations, and dynamic comfort score transitions

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeNavigation();
    initializeWeatherAnimations();
    initializeComfortScoreTransitions();
    initializeFormEnhancements();
    initializeScrollEffects();
    initializeLoadingStates();
    initializeAutoRefresh();
}

// Navigation enhancements
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    // Add scrolled class on scroll
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScrollY = currentScrollY;
    });

    // Add click ripple effect to navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

// Enhanced weather animations
function initializeWeatherAnimations() {
    // Animate weather icons based on conditions
    const weatherIcon = document.querySelector('.weather-icon');
    if (weatherIcon) {
        const iconText = weatherIcon.textContent;
        
        // Add specific animations based on weather
        if (iconText.includes('🌧️') || iconText.includes('⛈️')) {
            weatherIcon.style.animation = 'bounce 1s ease-in-out infinite';
        } else if (iconText.includes('☀️')) {
            weatherIcon.style.animation = 'rotate 20s linear infinite';
        } else if (iconText.includes('💨')) {
            weatherIcon.style.animation = 'sway 2s ease-in-out infinite';
        }
    }

    // Animate detail items on hover
    document.querySelectorAll('.detail-item').forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
        
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Dynamic comfort score color transitions
function initializeComfortScoreTransitions() {
    const comfortScore = document.querySelector('.comfort-score');
    const comfortNumber = document.querySelector('.comfort-number');
    
    if (comfortScore && comfortNumber) {
        const score = parseInt(comfortNumber.textContent);
        
        // Add dynamic glow effect based on score
        const glowIntensity = Math.min(score / 100, 1);
        const hue = score > 80 ? 200 : score > 60 ? 120 : score > 40 ? 60 : 0;
        
        comfortScore.style.boxShadow = `
            0 8px 32px rgba(${hue}, 150, 255, ${glowIntensity * 0.3}),
            0 0 20px rgba(${hue}, 150, 255, ${glowIntensity * 0.2})
        `;
        
        // Animate number counting effect
        animateNumber(comfortNumber, 0, score, 1500);
        
        // Add click effect for comfort score
        comfortScore.addEventListener('click', function() {
            this.style.animation = 'none';
            setTimeout(() => {
                this.style.animation = 'comfortGlow 2s ease-in-out infinite';
            }, 10);
            
            // Show comfort breakdown with animation
            showComfortBreakdown();
        });
    }
}

// Enhanced form interactions
function initializeFormEnhancements() {
    // Enhanced radio button interactions
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const groupName = this.name;
            
            // Remove active class from all cards in group
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                const card = r.closest('.option-card');
                card.classList.remove('active');
                card.style.transform = 'scale(1)';
            });
            
            // Add active class to selected card with animation
            const selectedCard = this.closest('.option-card');
            selectedCard.classList.add('active');
            
            // Animate selection
            selectedCard.style.transform = 'scale(1.05)';
            setTimeout(() => {
                selectedCard.style.transform = 'scale(1)';
            }, 200);
            
            // Create selection ripple effect
            createRippleEffect({ 
                clientX: selectedCard.offsetLeft + selectedCard.offsetWidth / 2,
                clientY: selectedCard.offsetTop + selectedCard.offsetHeight / 2
            }, selectedCard);
        });
    });

    // Enhanced temperature range inputs
    document.querySelectorAll('.range-input').forEach(input => {
        input.addEventListener('input', function() {
            validateTemperatureRange();
            updateTemperaturePreview();
        });
        
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Form submission enhancements
    const settingsForm = document.querySelector('.settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const submitBtn = document.querySelector('.save-btn');
            if (submitBtn) {
                submitBtn.innerHTML = '⏳ Saving...';
                submitBtn.style.transform = 'scale(0.95)';
                
                // Add saving animation
                submitBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2, #667eea, #764ba2)';
                submitBtn.style.backgroundSize = '300% 300%';
                submitBtn.style.animation = 'gradientShift 1s ease infinite';
            }
        });
    }
}

// Scroll-based animations
function initializeScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Add stagger effect for child elements
                const children = entry.target.querySelectorAll('.detail-item, .hour-item, .rec-card');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.style.opacity = '1';
                        child.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }
        });
    }, observerOptions);

    // Observe all major sections
    document.querySelectorAll('.weather-details, .forecast-section, .recommendations').forEach(section => {
        observer.observe(section);
    });
}

// Enhanced loading states
function initializeLoadingStates() {
    // Add loading states to buttons and forms
    document.querySelectorAll('.action-btn, .search-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.classList.contains('loading')) return;
            
            this.classList.add('loading');
            const originalText = this.innerHTML;
            
            // Create loading dots animation
            let dots = 0;
            const loadingInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                this.innerHTML = originalText.split(' ')[0] + '.'.repeat(dots);
            }, 300);
            
            // Reset after delay (or on actual response)
            setTimeout(() => {
                clearInterval(loadingInterval);
                this.classList.remove('loading');
                this.innerHTML = originalText;
            }, 2000);
        });
    });
}

// Auto-refresh with visual feedback
function initializeAutoRefresh() {
    let refreshTimer;
    const refreshInterval = 10 * 60 * 1000; // 10 minutes

    function scheduleRefresh() {
        refreshTimer = setTimeout(() => {
            if (document.visibilityState === 'visible') {
                showRefreshNotification();
            }
        }, refreshInterval);
    }

    function showRefreshNotification() {
        const notification = document.createElement('div');
        notification.className = 'refresh-notification';
        notification.innerHTML = `
            <div class="refresh-content">
                <span>🌬️</span>
                <p>Updating weather data...</p>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    // Clear timer on page hide
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            clearTimeout(refreshTimer);
        } else {
            scheduleRefresh();
        }
    });

    scheduleRefresh();
}

// Utility Functions

function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.className = 'ripple';

    element.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    const diff = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + diff * easeOutCubic);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function validateTemperatureRange() {
    const minInput = document.querySelector('input[name="temp_min"]');
    const maxInput = document.querySelector('input[name="temp_max"]');
    
    if (minInput && maxInput) {
        const min = parseInt(minInput.value);
        const max = parseInt(maxInput.value);
        
        if (min >= max) {
            minInput.style.borderColor = '#ff6b6b';
            maxInput.style.borderColor = '#ff6b6b';
            
            // Show validation message
            showValidationMessage('Minimum temperature must be less than maximum');
        } else {
            minInput.style.borderColor = '';
            maxInput.style.borderColor = '';
            hideValidationMessage();
        }
    }
}

function updateTemperaturePreview() {
    const minInput = document.querySelector('input[name="temp_min"]');
    const maxInput = document.querySelector('input[name="temp_max"]');
    const currentSetting = document.querySelector('.current-setting .current-value');
    
    if (minInput && maxInput && currentSetting) {
        const min = minInput.value || '18';
        const max = maxInput.value || '26';
        currentSetting.textContent = `${min}°C - ${max}°C`;
    }
}

function showComfortBreakdown() {
    const breakdown = document.querySelector('.rec-card');
    if (breakdown) {
        breakdown.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
        breakdown.style.color = 'white';
        breakdown.style.transform = 'scale(1.02)';
        
        setTimeout(() => {
            breakdown.style.background = '';
            breakdown.style.color = '';
            breakdown.style.transform = '';
        }, 2000);
    }
}

function showValidationMessage(message) {
    let msgElement = document.querySelector('.validation-message');
    
    if (!msgElement) {
        msgElement = document.createElement('div');
        msgElement.className = 'validation-message';
        msgElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #ff8a80, #ea4d2c);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(msgElement);
    }
    
    msgElement.textContent = message;
    
    clearTimeout(msgElement.hideTimeout);
    msgElement.hideTimeout = setTimeout(() => {
        hideValidationMessage();
    }, 3000);
}

function hideValidationMessage() {
    const msgElement = document.querySelector('.validation-message');
    if (msgElement) {
        msgElement.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            msgElement.remove();
        }, 300);
    }
}

// Enhanced feedback function with better UX
function provideFeedback(type) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    // Visual feedback
    btn.style.transform = 'scale(0.95)';
    btn.innerHTML = type === 'good' ? '✨ Thanks!' : '📝 Noted!';
    btn.style.background = type === 'good' ? 
        'linear-gradient(135deg, #4facfe, #00f2fe)' : 
        'linear-gradient(135deg, #ffecd2, #fcb69f)';
    btn.disabled = true;
    
    // Create success particle effect
    createParticleEffect(btn);
    
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'feedback=' + encodeURIComponent(type)
    })
    .then(response => response.json())
    .then(data => {
        // Show success message
        showNotification(data.message || 'Feedback received! VAYU is learning...', 'success');
        
        // Reset button after delay
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.transform = '';
            btn.disabled = false;
        }, 2000);
    })
    .catch(error => {
        console.error('Feedback error:', error);
        btn.innerHTML = '❌ Error';
        showNotification('Unable to send feedback. Please try again.', 'error');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.transform = '';
            btn.disabled = false;
        }, 2000);
    });
}

function createParticleEffect(element) {
    const rect = element.getBoundingClientRect();
    const colors = ['#4facfe', '#00f2fe', '#667eea', '#764ba2'];
    
    for (let i = 0; i < 6; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: 50%;
            left: ${rect.left + rect.width / 2}px;
            top: ${rect.top + rect.height / 2}px;
            pointer-events: none;
            z-index: 1000;
            animation: particle ${0.6 + Math.random() * 0.4}s ease-out forwards;
        `;
        
        const angle = (Math.PI * 2 * i) / 6;
        const distance = 50 + Math.random() * 30;
        
        particle.style.setProperty('--dx', Math.cos(angle) * distance + 'px');
        particle.style.setProperty('--dy', Math.sin(angle) * distance + 'px');
        
        document.body.appendChild(particle);
        
        setTimeout(() => particle.remove(), 1000);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: 'linear-gradient(135deg, #4facfe, #00f2fe)',
        error: 'linear-gradient(135deg, #ff8a80, #ea4d2c)',
        info: 'linear-gradient(135deg, #667eea, #764ba2)'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        z-index: 1000;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.4s cubic-bezier(0.22, 1, 0.36, 1);
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// Add required CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes particle {
        to {
            transform: translate(var(--dx), var(--dy));
            opacity: 0;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes sway {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(5deg); }
    }
    
    .refresh-notification {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        text-align: center;
        animation: fadeIn 0.5s ease;
    }
    
    .refresh-content span {
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
        animation: bounce 1s infinite;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
        to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
`;
=======
// Enhanced JavaScript for VAYU Weather App
// Adds smooth interactions, animations, and dynamic comfort score transitions

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeNavigation();
    initializeWeatherAnimations();
    initializeComfortScoreTransitions();
    initializeFormEnhancements();
    initializeScrollEffects();
    initializeLoadingStates();
    initializeAutoRefresh();
}

// Navigation enhancements
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    // Add scrolled class on scroll
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScrollY = currentScrollY;
    });

    // Add click ripple effect to navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

// Enhanced weather animations
function initializeWeatherAnimations() {
    // Animate weather icons based on conditions
    const weatherIcon = document.querySelector('.weather-icon');
    if (weatherIcon) {
        const iconText = weatherIcon.textContent;
        
        // Add specific animations based on weather
        if (iconText.includes('🌧️') || iconText.includes('⛈️')) {
            weatherIcon.style.animation = 'bounce 1s ease-in-out infinite';
        } else if (iconText.includes('☀️')) {
            weatherIcon.style.animation = 'rotate 20s linear infinite';
        } else if (iconText.includes('💨')) {
            weatherIcon.style.animation = 'sway 2s ease-in-out infinite';
        }
    }

    // Animate detail items on hover
    document.querySelectorAll('.detail-item').forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
        
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Dynamic comfort score color transitions
function initializeComfortScoreTransitions() {
    const comfortScore = document.querySelector('.comfort-score');
    const comfortNumber = document.querySelector('.comfort-number');
    
    if (comfortScore && comfortNumber) {
        const score = parseInt(comfortNumber.textContent);
        
        // Add dynamic glow effect based on score
        const glowIntensity = Math.min(score / 100, 1);
        const hue = score > 80 ? 200 : score > 60 ? 120 : score > 40 ? 60 : 0;
        
        comfortScore.style.boxShadow = `
            0 8px 32px rgba(${hue}, 150, 255, ${glowIntensity * 0.3}),
            0 0 20px rgba(${hue}, 150, 255, ${glowIntensity * 0.2})
        `;
        
        // Animate number counting effect
        animateNumber(comfortNumber, 0, score, 1500);
        
        // Add click effect for comfort score
        comfortScore.addEventListener('click', function() {
            this.style.animation = 'none';
            setTimeout(() => {
                this.style.animation = 'comfortGlow 2s ease-in-out infinite';
            }, 10);
            
            // Show comfort breakdown with animation
            showComfortBreakdown();
        });
    }
}

// Enhanced form interactions
function initializeFormEnhancements() {
    // Enhanced radio button interactions
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const groupName = this.name;
            
            // Remove active class from all cards in group
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                const card = r.closest('.option-card');
                card.classList.remove('active');
                card.style.transform = 'scale(1)';
            });
            
            // Add active class to selected card with animation
            const selectedCard = this.closest('.option-card');
            selectedCard.classList.add('active');
            
            // Animate selection
            selectedCard.style.transform = 'scale(1.05)';
            setTimeout(() => {
                selectedCard.style.transform = 'scale(1)';
            }, 200);
            
            // Create selection ripple effect
            createRippleEffect({ 
                clientX: selectedCard.offsetLeft + selectedCard.offsetWidth / 2,
                clientY: selectedCard.offsetTop + selectedCard.offsetHeight / 2
            }, selectedCard);
        });
    });

    // Enhanced temperature range inputs
    document.querySelectorAll('.range-input').forEach(input => {
        input.addEventListener('input', function() {
            validateTemperatureRange();
            updateTemperaturePreview();
        });
        
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Form submission enhancements
    const settingsForm = document.querySelector('.settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const submitBtn = document.querySelector('.save-btn');
            if (submitBtn) {
                submitBtn.innerHTML = '⏳ Saving...';
                submitBtn.style.transform = 'scale(0.95)';
                
                // Add saving animation
                submitBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2, #667eea, #764ba2)';
                submitBtn.style.backgroundSize = '300% 300%';
                submitBtn.style.animation = 'gradientShift 1s ease infinite';
            }
        });
    }
}

// Scroll-based animations
function initializeScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Add stagger effect for child elements
                const children = entry.target.querySelectorAll('.detail-item, .hour-item, .rec-card');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.style.opacity = '1';
                        child.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }
        });
    }, observerOptions);

    // Observe all major sections
    document.querySelectorAll('.weather-details, .forecast-section, .recommendations').forEach(section => {
        observer.observe(section);
    });
}

// Enhanced loading states
function initializeLoadingStates() {
    // Add loading states to buttons and forms
    document.querySelectorAll('.action-btn, .search-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.classList.contains('loading')) return;
            
            this.classList.add('loading');
            const originalText = this.innerHTML;
            
            // Create loading dots animation
            let dots = 0;
            const loadingInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                this.innerHTML = originalText.split(' ')[0] + '.'.repeat(dots);
            }, 300);
            
            // Reset after delay (or on actual response)
            setTimeout(() => {
                clearInterval(loadingInterval);
                this.classList.remove('loading');
                this.innerHTML = originalText;
            }, 2000);
        });
    });
}

// Auto-refresh with visual feedback
function initializeAutoRefresh() {
    let refreshTimer;
    const refreshInterval = 10 * 60 * 1000; // 10 minutes

    function scheduleRefresh() {
        refreshTimer = setTimeout(() => {
            if (document.visibilityState === 'visible') {
                showRefreshNotification();
            }
        }, refreshInterval);
    }

    function showRefreshNotification() {
        const notification = document.createElement('div');
        notification.className = 'refresh-notification';
        notification.innerHTML = `
            <div class="refresh-content">
                <span>🌬️</span>
                <p>Updating weather data...</p>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    // Clear timer on page hide
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            clearTimeout(refreshTimer);
        } else {
            scheduleRefresh();
        }
    });

    scheduleRefresh();
}

// Utility Functions

function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.className = 'ripple';

    element.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    const diff = end - start;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + diff * easeOutCubic);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function validateTemperatureRange() {
    const minInput = document.querySelector('input[name="temp_min"]');
    const maxInput = document.querySelector('input[name="temp_max"]');
    
    if (minInput && maxInput) {
        const min = parseInt(minInput.value);
        const max = parseInt(maxInput.value);
        
        if (min >= max) {
            minInput.style.borderColor = '#ff6b6b';
            maxInput.style.borderColor = '#ff6b6b';
            
            // Show validation message
            showValidationMessage('Minimum temperature must be less than maximum');
        } else {
            minInput.style.borderColor = '';
            maxInput.style.borderColor = '';
            hideValidationMessage();
        }
    }
}

function updateTemperaturePreview() {
    const minInput = document.querySelector('input[name="temp_min"]');
    const maxInput = document.querySelector('input[name="temp_max"]');
    const currentSetting = document.querySelector('.current-setting .current-value');
    
    if (minInput && maxInput && currentSetting) {
        const min = minInput.value || '18';
        const max = maxInput.value || '26';
        currentSetting.textContent = `${min}°C - ${max}°C`;
    }
}

function showComfortBreakdown() {
    const breakdown = document.querySelector('.rec-card');
    if (breakdown) {
        breakdown.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
        breakdown.style.color = 'white';
        breakdown.style.transform = 'scale(1.02)';
        
        setTimeout(() => {
            breakdown.style.background = '';
            breakdown.style.color = '';
            breakdown.style.transform = '';
        }, 2000);
    }
}

function showValidationMessage(message) {
    let msgElement = document.querySelector('.validation-message');
    
    if (!msgElement) {
        msgElement = document.createElement('div');
        msgElement.className = 'validation-message';
        msgElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #ff8a80, #ea4d2c);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(msgElement);
    }
    
    msgElement.textContent = message;
    
    clearTimeout(msgElement.hideTimeout);
    msgElement.hideTimeout = setTimeout(() => {
        hideValidationMessage();
    }, 3000);
}

function hideValidationMessage() {
    const msgElement = document.querySelector('.validation-message');
    if (msgElement) {
        msgElement.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            msgElement.remove();
        }, 300);
    }
}

// Enhanced feedback function with better UX
function provideFeedback(type) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    // Visual feedback
    btn.style.transform = 'scale(0.95)';
    btn.innerHTML = type === 'good' ? '✨ Thanks!' : '📝 Noted!';
    btn.style.background = type === 'good' ? 
        'linear-gradient(135deg, #4facfe, #00f2fe)' : 
        'linear-gradient(135deg, #ffecd2, #fcb69f)';
    btn.disabled = true;
    
    // Create success particle effect
    createParticleEffect(btn);
    
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'feedback=' + encodeURIComponent(type)
    })
    .then(response => response.json())
    .then(data => {
        // Show success message
        showNotification(data.message || 'Feedback received! VAYU is learning...', 'success');
        
        // Reset button after delay
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.transform = '';
            btn.disabled = false;
        }, 2000);
    })
    .catch(error => {
        console.error('Feedback error:', error);
        btn.innerHTML = '❌ Error';
        showNotification('Unable to send feedback. Please try again.', 'error');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
            btn.style.transform = '';
            btn.disabled = false;
        }, 2000);
    });
}

function createParticleEffect(element) {
    const rect = element.getBoundingClientRect();
    const colors = ['#4facfe', '#00f2fe', '#667eea', '#764ba2'];
    
    for (let i = 0; i < 6; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            border-radius: 50%;
            left: ${rect.left + rect.width / 2}px;
            top: ${rect.top + rect.height / 2}px;
            pointer-events: none;
            z-index: 1000;
            animation: particle ${0.6 + Math.random() * 0.4}s ease-out forwards;
        `;
        
        const angle = (Math.PI * 2 * i) / 6;
        const distance = 50 + Math.random() * 30;
        
        particle.style.setProperty('--dx', Math.cos(angle) * distance + 'px');
        particle.style.setProperty('--dy', Math.sin(angle) * distance + 'px');
        
        document.body.appendChild(particle);
        
        setTimeout(() => particle.remove(), 1000);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: 'linear-gradient(135deg, #4facfe, #00f2fe)',
        error: 'linear-gradient(135deg, #ff8a80, #ea4d2c)',
        info: 'linear-gradient(135deg, #667eea, #764ba2)'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        z-index: 1000;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.4s cubic-bezier(0.22, 1, 0.36, 1);
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// Add required CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes particle {
        to {
            transform: translate(var(--dx), var(--dy));
            opacity: 0;
        }
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes sway {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(5deg); }
    }
    
    .refresh-notification {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        text-align: center;
        animation: fadeIn 0.5s ease;
    }
    
    .refresh-content span {
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
        animation: bounce 1s infinite;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
        to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
`;
>>>>>>> 4e64647e8d487574b60f65888c9d2c47f4ce8cd4
document.head.appendChild(style);