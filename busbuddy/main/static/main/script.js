// script.js
// Simple interactivity: mobile menu toggle + accessible dropdown keyboard support

document.addEventListener('DOMContentLoaded', function () {
  // mobile menu toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  mobileToggle && mobileToggle.addEventListener('click', function () {
    const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
    mobileToggle.setAttribute('aria-expanded', String(!expanded));
    mobileMenu.setAttribute('aria-hidden', String(expanded));
    mobileMenu.style.display = expanded ? 'none' : 'block';
  });

  // make nav buttons toggleable by keyboard (space/enter)
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!expanded));
        // toggle dropdown manually for keyboard users
        const parent = btn.parentElement;
        const dd = parent.querySelector('.dropdown');
        if (dd) {
          if (!expanded) {
            dd.style.display = 'block';
          } else {
            dd.style.display = 'none';
          }
        }
      }
    });

    // ensure mouse click also toggles (useful for touch devices)
    btn.addEventListener('click', (e) => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      const parent = btn.parentElement;
      const dd = parent.querySelector('.dropdown');
      if (dd) {
        dd.style.display = expanded ? 'none' : 'block';
        // hide dropdown after clicking away
        setTimeout(() => {
          const onDoc = (ev) => {
            if (!parent.contains(ev.target)) {
              dd.style.display = 'none';
              btn.setAttribute('aria-expanded','false');
              document.removeEventListener('click', onDoc);
            }
          };
          document.addEventListener('click', onDoc);
        }, 0);
      }
    });
  });

  // close open dropdowns when resizing to mobile
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 980) {
      document.querySelectorAll('.dropdown').forEach(dd => dd.style.display = '');
      document.querySelectorAll('.nav-btn').forEach(n => n.setAttribute('aria-expanded','false'));
    }
  });
});
