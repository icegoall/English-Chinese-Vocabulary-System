/* ===========================================================================
   English Vocabulary System — Client-side JavaScript
   Handles the mobile navigation toggle (shared across all pages).
   Page-specific logic is embedded in each template's {% block scripts %}.
   =========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation toggle
    var navToggle = document.getElementById('navToggle');
    var navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });

        // Close menu when a link is clicked (mobile)
        navMenu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navMenu.classList.remove('active');
            });
        });
    }
});
