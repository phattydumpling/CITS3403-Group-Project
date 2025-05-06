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
    const toggle = document.getElementById('darkModeToggle');
    const dot = document.querySelector('.dot'); // the small circle

    if (toggle) {
        toggle.addEventListener('change', function () {
            document.body.classList.toggle('dark-mode');

            // Move the dot
            if (toggle.checked) {
                dot.classList.add('translate-x-4');
            } else {
                dot.classList.remove('translate-x-4');
            }
        });
    }

    // =====================
    // Navbar toggle for mobile
    // =====================
    document.getElementById('nav-toggle').addEventListener('click', function () {
        const navContent = document.getElementById('nav-content');
        navContent.classList.toggle('hidden');
    });

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
                    }, 300); // Match this with the CSS transition duration
                } else {
                    // If page content not found, navigate immediately
                    window.location.href = targetUrl;
                }
            }
        });
    });
});