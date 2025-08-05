// Bo Rangers FC Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeComponents();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
});

function initializeComponents() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
    });
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize form validations
    initializeFormValidations();
}

function setupEventListeners() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            // Skip if href is just '#' or empty
            if (href && href !== '#' && href.length > 1) {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
    
    // Search functionality
    setupSearchFunctionality();
    
    // Real-time updates for live matches
    setupLiveUpdates();
}

function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeLoadingStates() {
    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
}

function initializeFormValidations() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
    
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.name === 'password1' || input.name === 'password') {
            input.addEventListener('input', function() {
                showPasswordStrength(this);
            });
        }
    });
}

function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(input.value);
    
    if (input.value && !isValid) {
        input.classList.add('is-invalid');
        showFieldError(input, 'Please enter a valid email address');
    } else {
        input.classList.remove('is-invalid');
        hideFieldError(input);
    }
}

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Format for Sierra Leone numbers
    if (value.length > 0) {
        if (value.startsWith('232')) {
            value = value.substring(0, 12);
        } else if (value.startsWith('0')) {
            value = '232' + value.substring(1);
            value = value.substring(0, 12);
        } else {
            value = '232' + value;
            value = value.substring(0, 12);
        }
    }
    
    input.value = value;
}

function showPasswordStrength(input) {
    const password = input.value;
    const strength = calculatePasswordStrength(password);
    
    let strengthIndicator = input.parentNode.querySelector('.password-strength');
    if (!strengthIndicator) {
        strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength mt-1';
        input.parentNode.appendChild(strengthIndicator);
    }
    
    const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    if (password.length > 0) {
        strengthIndicator.innerHTML = `
            <div class="progress" style="height: 5px;">
                <div class="progress-bar bg-${strengthColors[strength]}" 
                     style="width: ${(strength + 1) * 20}%"></div>
            </div>
            <small class="text-${strengthColors[strength]}">Password strength: ${strengthText[strength]}</small>
        `;
    } else {
        strengthIndicator.innerHTML = '';
    }
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.match(/[a-z]/)) score++;
    if (password.match(/[A-Z]/)) score++;
    if (password.match(/[0-9]/)) score++;
    if (password.match(/[^a-zA-Z0-9]/)) score++;
    
    return Math.min(score, 4);
}

function showFieldError(input, message) {
    hideFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
}

function hideFieldError(input) {
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        let searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.searchTarget);
            }, 300);
        });
    });
}

function performSearch(query, target) {
    // Basic client-side search functionality
    if (!query || !target) return;
    
    const searchableElements = document.querySelectorAll(`[data-searchable="${target}"]`);
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const matches = text.includes(query.toLowerCase());
        
        if (matches) {
            element.style.display = '';
            element.classList.remove('search-hidden');
        } else {
            element.style.display = 'none';
            element.classList.add('search-hidden');
        }
    });
}

function setupLiveUpdates() {
    // Check for live matches and set up auto-refresh
    const liveMatchElements = document.querySelectorAll('.badge.bg-danger');
    const hasLiveMatches = Array.from(liveMatchElements).some(el => 
        el.textContent.includes('Live') || el.textContent.includes('live')
    );
    
    if (hasLiveMatches) {
        // Refresh every 30 seconds for live matches
        setTimeout(() => {
            location.reload();
        }, 30000);
        
        // Show live indicator
        showLiveIndicator();
    }
}

function showLiveIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'live-indicator position-fixed top-0 end-0 m-3';
    indicator.innerHTML = `
        <div class="badge bg-danger">
            <i class="bi bi-broadcast"></i> LIVE
        </div>
    `;
    indicator.style.zIndex = '1050';
    document.body.appendChild(indicator);
}

// Utility Functions
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Copied to clipboard!', 'success');
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other scripts
window.BoRangersFC = {
    showNotification,
    copyToClipboard,
    formatCurrency,
    formatDate,
    debounce
};

// Service Worker Registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}

