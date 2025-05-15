// Tailwind Configuration
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#173B64',
                secondary: '#A3C4EB',
                accent: '#FFDE70',
                background: '#F6FAFF',
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', function () {

    // =====================
    // Navbar toggle for mobile
    // =====================
    const burger = document.getElementById('navbar-burger');
    const menu = document.getElementById('navbar-menu');
    if (burger && menu) {
        burger.addEventListener('click', function() {
            menu.classList.add('open');
            menu.classList.remove('opacity-0', 'pointer-events-none');
            menu.classList.add('opacity-100', 'pointer-events-auto');
        });
        // Close menu when clicking the close button
        const closeBtn = menu.querySelector('#navbar-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                menu.classList.remove('open');
                setTimeout(() => {
                    menu.classList.remove('opacity-100', 'pointer-events-auto');
                    menu.classList.add('opacity-0', 'pointer-events-none');
                }, 300);
            });
        }
        // Close menu when clicking the overlay (but not the sidebar itself)
        menu.addEventListener('click', function(e) {
            if (e.target === menu) {
                menu.classList.remove('open');
                setTimeout(() => {
                    menu.classList.remove('opacity-100', 'pointer-events-auto');
                    menu.classList.add('opacity-0', 'pointer-events-none');
                }, 300);
            }
        });
    }

    // Delete Account Modal functionality
    const deleteAccountForm = document.getElementById('deleteAccountForm');
    const deleteAccountModal = document.getElementById('deleteAccountModal');
    
    if (deleteAccountForm && deleteAccountModal) {
        window.showDeleteConfirmation = function() {
            deleteAccountModal.classList.remove('hidden');
        };

        window.hideDeleteConfirmation = function() {
            deleteAccountModal.classList.add('hidden');
        };

        window.confirmDelete = function() {
            deleteAccountForm.submit();
        };

        // Close modal when clicking outside
        deleteAccountModal.addEventListener('click', (e) => {
            if (e.target === deleteAccountModal) {
                hideDeleteConfirmation();
            }
        });
    }

    // Page Transitions
    const navLinks = document.querySelectorAll('nav a');
    const pageContent = document.querySelector('.page-content');
    
    // Handle initial page load
    if (pageContent) {
        // Remove fade-out class if it exists
        pageContent.classList.remove('fade-out');
    }
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only handle internal links
            if (this.href.startsWith(window.location.origin)) {
                e.preventDefault();
                const targetUrl = this.href;
                
                // Add fade-out class to trigger the transition
                if (pageContent) {
                    pageContent.classList.add('fade-out');
                    
                    // Wait for the fade-out animation to complete before navigating
                    setTimeout(() => {
                        window.location.href = targetUrl;
                    }, 100); // Match this with the CSS transition duration
                } else {
                    // If page content not found, navigate immediately
                    window.location.href = targetUrl;
                }
            }
        });
    });

    // Close mobile menu on resize to desktop (now 1024px)
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 1024 && menu) {
            menu.classList.remove('open');
            setTimeout(() => {
                menu.classList.remove('opacity-100', 'pointer-events-auto');
                menu.classList.add('opacity-0', 'pointer-events-none');
            }, 300);
        }
    });

    // Password validation functionality
    const password = document.getElementById('password');
    if (!password) return; // Exit if password field doesn't exist

    const requirements = {
        length: document.getElementById('length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        number: document.getElementById('number'),
        special: document.getElementById('special')
    };

    function updateRequirement(requirement, isValid) {
        if (!requirement) return; // Exit if requirement element doesn't exist
        const icon = requirement.querySelector('.requirement-icon i');
        if (!icon) return; // Exit if icon doesn't exist

        if (isValid) {
            requirement.classList.add('valid');
            requirement.classList.remove('invalid');
            icon.className = 'fas fa-check';
        } else {
            requirement.classList.add('invalid');
            requirement.classList.remove('valid');
            icon.className = 'fas fa-times';
        }
    }

    password.addEventListener('input', function() {
        const value = this.value;
        
        // Check length
        updateRequirement(requirements.length, value.length >= 8);

        // Check uppercase
        updateRequirement(requirements.uppercase, /[A-Z]/.test(value));

        // Check lowercase
        updateRequirement(requirements.lowercase, /[a-z]/.test(value));

        // Check number
        updateRequirement(requirements.number, /\d/.test(value));

        // Check special character
        updateRequirement(requirements.special, /[!@#$%^&*(),.?":{}|<>]/.test(value));
    });
});