/* ================================================
   FORREST ANALYTICS GROUP — SCRIPTS
   ================================================ */

/* ── Navbar: transparent → solid on scroll ── */
const navbar = document.getElementById('navbar');

function updateNav() {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}
window.addEventListener('scroll', updateNav, { passive: true });
updateNav();

/* ── Mobile Menu ── */
const toggle = document.getElementById('nav-toggle');
const menu   = document.getElementById('nav-menu');

toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!open));
  menu.classList.toggle('open', !open);
});

// Close on nav link click
menu.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', 'false');
    menu.classList.remove('open');
  });
});

// Close on outside click
document.addEventListener('click', (e) => {
  if (!navbar.contains(e.target) && menu.classList.contains('open')) {
    toggle.setAttribute('aria-expanded', 'false');
    menu.classList.remove('open');
  }
});

/* ── Smooth Scroll with nav offset ── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const id = this.getAttribute('href');
    if (id === '#') return;
    const target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    const navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 72;
    const top = target.getBoundingClientRect().top + window.scrollY - navH - 12;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});

/* ── Scroll Reveal (Intersection Observer) ── */
const revealEls = document.querySelectorAll('[data-reveal]');

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    // Stagger siblings within same parent
    const siblings = Array.from(entry.target.parentElement.querySelectorAll('[data-reveal]'));
    const idx = siblings.indexOf(entry.target);
    setTimeout(() => {
      entry.target.classList.add('revealed');
    }, idx * 100);
    revealObserver.unobserve(entry.target);
  });
}, { threshold: 0.08, rootMargin: '0px 0px -48px 0px' });

revealEls.forEach(el => revealObserver.observe(el));

/* ── FAQ Accordion ── */
document.querySelectorAll('.faq-q').forEach(button => {
  button.addEventListener('click', () => {
    const isOpen = button.getAttribute('aria-expanded') === 'true';

    // Close all
    document.querySelectorAll('.faq-q').forEach(btn => {
      btn.setAttribute('aria-expanded', 'false');
      btn.nextElementSibling.hidden = true;
    });

    // Open clicked (unless it was already open)
    if (!isOpen) {
      button.setAttribute('aria-expanded', 'true');
      button.nextElementSibling.hidden = false;
    }
  });
});

/* ── Calendly Badge Widget (floats on every page) ── */
(function () {
  var css = document.createElement('link');
  css.rel = 'stylesheet';
  css.href = 'https://assets.calendly.com/assets/external/widget.css';
  document.head.appendChild(css);

  // Only load the script if it isn't already on the page (inline embed pages load it too)
  if (!document.querySelector('script[src*="calendly.com/assets/external/widget.js"]')) {
    var js = document.createElement('script');
    js.src = 'https://assets.calendly.com/assets/external/widget.js';
    js.async = true;
    js.onload = initBadge;
    document.head.appendChild(js);
  } else {
    // Script already present (inline embed page) — wait for it to finish loading
    window.addEventListener('load', initBadge);
  }

  function initBadge() {
    if (typeof Calendly !== 'undefined') {
      Calendly.initBadgeWidget({
        url: 'https://calendly.com/jf10747454-sju/30min',
        text: 'Book a Free 30-Min Call',
        color: '#C9A84C',
        textColor: '#ffffff',
        branding: false
      });
    }
  }
})();

/* ── Contact Form (Formspree) ── */
const form       = document.getElementById('contact-form');
const submitBtn  = document.getElementById('submit-btn');
const successMsg = document.getElementById('form-success');

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name    = form.querySelector('#name').value.trim();
    const email   = form.querySelector('#email').value.trim();
    const message = form.querySelector('#message').value.trim();
    if (!name || !email || !message) return;

    // Loading state
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display    = 'none';
    submitBtn.querySelector('.btn-loading').style.display = 'inline';

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'Accept': 'application/json' }
      });

      if (res.ok) {
        form.hidden       = true;
        successMsg.hidden = false;
      } else {
        throw new Error('Server error');
      }
    } catch {
      submitBtn.disabled = false;
      submitBtn.querySelector('.btn-text').style.display    = 'inline';
      submitBtn.querySelector('.btn-loading').style.display = 'none';
      alert('Something went wrong. Please email us directly at jf10747454@sju.edu');
    }
  });
}
