// Global JavaScript for StockSense AI

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 StockSense AI loaded successfully!');

    // Initialize common functionality
    initializeDateInput();
    initializeFlashMessages();
    initializeCloseButtons();
    initializeFormSubmissions();
    initializePasswordToggles();
    initializeFilterChips();
    initializeSmoothScrolling();
    initializeTimeframeDropdown();
    initializeAnalysisTimeframe();

    // Performance monitoring
    window.addEventListener('load', function() {
        console.log(`⚡ Page loaded in ${Math.round(performance.now())}ms`);
    });
});

// Initialize date input for analysis forms
function initializeDateInput() {
    // existing id-based date input: only set valueAsDate when it's a date input
    const dateInput = document.getElementById('date');
    if (dateInput && dateInput.tagName === 'INPUT' && dateInput.type === 'date') {
        try {
            dateInput.valueAsDate = new Date();
        } catch (e) {
            // ignore if browser doesn't support valueAsDate
        }
    }

    // also support inputs that use the .date-input class (watchlist and other pages)
    const dateInputs = document.querySelectorAll('.date-input');
    dateInputs.forEach(function(el) {
        if (!el.value) {
            el.value = new Date().toISOString().split('T')[0];
        }
    });
}

// Timeframe dropdown for news filtering
function initializeTimeframeDropdown() {
    const tf = document.getElementById('timeframe');
    if (!tf) return;

    // When user changes timeframe, compute from/to ISO strings and reload page
    tf.addEventListener('change', function() {
        const now = new Date();

        // We'll construct explicit UTC moments for start/end so ranges nest correctly
        let fromDateUTC, toDateUTC;

        switch (tf.value) {
            case 'last_hour':
                // last 60 minutes till now
                fromDateUTC = new Date(Date.now() - 60 * 60 * 1000);
                toDateUTC = new Date();
                break;
            case 'today':
                fromDateUTC = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0));
                toDateUTC = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999));
                break;
            case 'this_week':
                fromDateUTC = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                toDateUTC = new Date();
                break;
            case 'this_month':
                fromDateUTC = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
                toDateUTC = new Date();
                break;
            case 'this_year':
                fromDateUTC = new Date(Date.UTC(now.getFullYear(), 0, 1, 0, 0, 0, 0));
                toDateUTC = new Date(Date.UTC(now.getFullYear(), 11, 31, 23, 59, 59, 999));
                break;
            default:
                fromDateUTC = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0));
                toDateUTC = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999));
        }

        // Build ISO strings (already in UTC because we used Date.UTC or Date.now())
        const fromIso = fromDateUTC.toISOString();
        const toIso = toDateUTC.toISOString();

        // Reload page with query params so server can use them
        const params = new URLSearchParams(window.location.search);
        params.set('from', fromIso);
        params.set('to', toIso);
        window.location.search = params.toString();
    });

    // If URL already has from/to params, try to pick matching option and show range label
    const params = new URLSearchParams(window.location.search);
    const fromParam = params.get('from');
    const toParam = params.get('to');
    if (fromParam && toParam) {
        // Simple heuristic: compute a best-match for the dropdown by comparing durations
        try {
            const from = new Date(fromParam);
            const to = new Date(toParam);
            const diffMs = to - from;
            const hours = diffMs / (1000 * 60 * 60);

            if (hours <= 1.5) tf.value = 'last_hour';
            else if (hours <= 24.5) tf.value = 'today';
            else if (hours <= 24*7 + 1) tf.value = 'this_week';
            else if (hours <= 24*30 + 2) tf.value = 'this_month';
            else tf.value = 'this_year';

            // Show human readable range if element present
            const rangeLabel = document.getElementById('timeframe-range');
            if (rangeLabel) {
                rangeLabel.textContent = `${from.toLocaleString()} — ${to.toLocaleString()}`;
                rangeLabel.style.display = 'block';
            }
        } catch (e) {
            // ignore
        }
    }
}

// Initialize the Analysis timeframe dropdown on the index form
function initializeAnalysisTimeframe() {
    const tf = document.getElementById('analysis_timeframe');
    const hiddenDate = document.getElementById('date');
    if (!tf || !hiddenDate) return;

    // For relative timeframes, keep the hidden date empty so server can use
    // the timeframe key (e.g. 'today', 'last_hour'). If you need a concrete
    // specific date value, change this behavior to populate hiddenDate.value.
    function clearHiddenDate() {
        hiddenDate.value = '';
    }

    // On load clear hidden date (we rely on analysis_timeframe param)
    clearHiddenDate();

    // Update hidden date when user changes selection (keep it empty)
    tf.addEventListener('change', function() {
        clearHiddenDate();
    });

    // Ensure that form submission uses the current dropdown value (the select
    // already has name=analysis_timeframe, but we ensure hidden date is cleared
    // just before submit so backend falls back to the timeframe key)
    const analysisForm = document.querySelector('.analysis-form');
    if (analysisForm) {
        analysisForm.addEventListener('submit', function() {
            // Clear hidden date; backend will read request.form['analysis_timeframe']
            clearHiddenDate();
        });
    }
}

// Initialize flash message auto-hide
function initializeFlashMessages() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
}

// Initialize close buttons for alerts
function initializeCloseButtons() {
    const closeBtns = document.querySelectorAll('.closebtn');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 500);
        });
    });
}

// Initialize form submissions with loading states
function initializeFormSubmissions() {
    const forms = document.querySelectorAll('.auth-form, .analysis-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.auth-submit, .btn-primary[type="submit"]');
            if (submitBtn) {
                const btnText = submitBtn.querySelector('.btn-text') || submitBtn;
                const btnLoader = submitBtn.querySelector('.btn-loader');

                if (btnLoader) {
                    btnText.style.display = 'none';
                    btnLoader.style.display = 'inline-flex';
                }
                submitBtn.disabled = true;
            }
        });
    });
}

// Initialize password toggle functionality
function initializePasswordToggles() {
    const toggles = document.querySelectorAll('.password-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input[type="password"], input[type="text"]');
            const icon = this.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });
    });
}

// Initialize filter chips for news/articles
function initializeFilterChips() {
    const filterChips = document.querySelectorAll('.filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            // Remove active class from all chips
            filterChips.forEach(c => c.classList.remove('active'));
            // Add active class to clicked chip
            this.classList.add('active');

            // Get filter value
            const filterValue = this.dataset.filter;

            // Filter news cards
            filterNewsCards(filterValue);
        });
    });
}

// Filter news cards based on sentiment
function filterNewsCards(sentiment) {
    const cards = document.querySelectorAll('.news-card');
    cards.forEach(card => {
        const cardSentiment = card.dataset.sentiment;
        if (sentiment === 'all' || cardSentiment === sentiment) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Initialize smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

// Fill company name in search input
function fillCompany(companyName) {
    const companyInput = document.getElementById('company');
    if (companyInput) {
        companyInput.value = companyName;
        companyInput.focus();
    }
}

// Focus on username field (for login page)
function focusUsername() {
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        usernameInput.focus();
    }
}

// Call focusUsername if on login page
if (document.getElementById('username')) {
    focusUsername();
}

// Initialize register form if present
if (document.getElementById('registerForm')) {
    initializeRegisterForm();
}

// Initialize register form functionality
function initializeRegisterForm() {
    // Focus on full name field
    document.getElementById('full_name').focus();

    // Password strength validation
    function validatePassword(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        return requirements;
    }

    // Email validation
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Real-time password validation
    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const password = this.value;
            const requirements = validatePassword(password);
            const requirementsList = document.querySelectorAll('.password-requirements li');

            requirementsList.forEach((item, index) => {
                const reqKeys = ['length', 'uppercase', 'lowercase', 'number', 'special'];
                if (requirements[reqKeys[index]]) {
                    item.style.color = '#22c55e';
                } else {
                    item.style.color = '#ef4444';
                }
            });
        });
    }

    // Form validation
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const fullNameField = document.getElementById('full_name');
            const usernameField = document.getElementById('username');
            const emailField = document.getElementById('email');
            const passwordField = document.getElementById('password');
            const confirmPasswordField = document.getElementById('confirm_password');

            let isValid = true;

            // Reset previous validation styles
            [fullNameField, usernameField, emailField, passwordField, confirmPasswordField].forEach(field => {
                if (field) field.classList.remove('is-invalid', 'is-valid');
            });

            // Validate full name
            if (fullNameField && fullNameField.value.trim().length < 2) {
                fullNameField.classList.add('is-invalid');
                isValid = false;
            } else if (fullNameField) {
                fullNameField.classList.add('is-valid');
            }

            // Validate username
            if (usernameField && usernameField.value.trim().length < 3) {
                usernameField.classList.add('is-invalid');
                isValid = false;
            } else if (usernameField) {
                usernameField.classList.add('is-valid');
            }

            // Validate email
            if (emailField && !validateEmail(emailField.value)) {
                emailField.classList.add('is-invalid');
                isValid = false;
            } else if (emailField) {
                emailField.classList.add('is-valid');
            }

            // Validate password
            if (passwordField) {
                const requirements = validatePassword(passwordField.value);
                const allRequirementsMet = Object.values(requirements).every(req => req);

                if (!allRequirementsMet) {
                    passwordField.classList.add('is-invalid');
                    isValid = false;
                } else {
                    passwordField.classList.add('is-valid');
                }
            }

            // Validate password confirmation
            if (passwordField && confirmPasswordField && passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.classList.add('is-invalid');
                isValid = false;
            } else if (confirmPasswordField && confirmPasswordField.value.length > 0) {
                confirmPasswordField.classList.add('is-valid');
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }
}

// Additional utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.flash-container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <span class="closebtn" onclick="this.parentElement.remove()">&times;</span>
    `;
    alertContainer.appendChild(alertDiv);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateX(100%)';
        setTimeout(() => alertDiv.remove(), 500);
    }, 5000);
}

// Debounce function for search inputs
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

// Export functions for global use
window.fillCompany = fillCompany;
window.filterNews = filterNewsCards;
window.showAlert = showAlert;
window.debounce = debounce;
