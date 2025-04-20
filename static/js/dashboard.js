// darkmode.js

document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    toggle.addEventListener('change', function () {
        document.body.classList.toggle('dark-mode');
    });
});
