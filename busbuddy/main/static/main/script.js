// script.js
// Simple interactivity: mobile menu toggle + accessible dropdown keyboard support

document.addEventListener('DOMContentLoaded', function () {
  const mobileToggle = document.getElementById('mobile-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', function () {
      const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', String(!expanded));
      mobileMenu.setAttribute('aria-hidden', String(expanded));
      mobileMenu.style.display = expanded ? 'none' : 'block';
    });
  }

  document.querySelectorAll('.nav-btn').forEach(btn => {
    const toggleDropdown = (btn) => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      const parent = btn.parentElement;
      const dd = parent && parent.querySelector('.dropdown');
      if (!dd) return;
      if (!expanded) {
        dd.style.display = 'block';
        btn.setAttribute('aria-expanded', 'true');
        const onDocClick = (ev) => {
          if (!parent.contains(ev.target)) {
            dd.style.display = 'none';
            btn.setAttribute('aria-expanded', 'false');
            document.removeEventListener('click', onDocClick);
          }
        };
        setTimeout(() => document.addEventListener('click', onDocClick), 0);
      } else {
        dd.style.display = 'none';
        btn.setAttribute('aria-expanded', 'false');
      }
    };

    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleDropdown(btn);
      }
    });

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleDropdown(btn);
    });
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth <= 980) {
      document.querySelectorAll('.dropdown').forEach(dd => dd.style.display = '');
      document.querySelectorAll('.nav-btn').forEach(n => n.setAttribute('aria-expanded','false'));
    }
  });
});
