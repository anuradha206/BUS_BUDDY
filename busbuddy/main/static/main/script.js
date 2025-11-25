// script.js
// Simple interactivity: mobile menu toggle + accessible dropdown keyboard support

document.addEventListener('DOMContentLoaded', function () {
  const mobileToggle = document.getElementById("mobile-toggle");
  const mobileMenu = document.getElementById("mobile-menu");

  mobileToggle.addEventListener("click", () => {
    const isOpen = mobileMenu.classList.toggle("open");
    mobileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
});
  
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', function () {
      const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', String(!expanded));
      mobileMenu.setAttribute('aria-hidden', String(expanded));
      mobileMenu.style.display = expanded ? 'none' : 'block';
    });
  }



  window.addEventListener('resize', () => {
    if (window.innerWidth <= 980) {
      document.querySelectorAll('.dropdown').forEach(dd => dd.style.display = '');
      document.querySelectorAll('.nav-btn').forEach(n => n.setAttribute('aria-expanded','false'));
    }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("stops-container");
  const addBtn = document.getElementById("add-stop");

  addBtn.addEventListener("click", function () {
    const newField = document.createElement("div");
    newField.classList.add("stop-field");
    newField.style.marginTop = "8px";

    newField.innerHTML = `
      <input type="text" name="stops[]" class="form-control" placeholder="Stop name">
    `;

    container.appendChild(newField);
  });
});

