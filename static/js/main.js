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
});