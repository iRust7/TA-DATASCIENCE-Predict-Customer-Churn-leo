/**
 * Veltrix – main.js
 * Minimal, focused JavaScript for UI enhancements.
 * No frameworks required – vanilla JS only.
 */

/* ── Run after DOM is fully loaded ─────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  initNavbarScroll();
  initFlashAutoDismiss();
  initActiveNavLink();
  initFadeInCards();
});


/* ================================================================
   1. Navbar – add "scrolled" class after user scrolls down
      (changes background opacity, adds shadow – see style.css)
   ================================================================ */
function initNavbarScroll() {
  const navbar = document.getElementById("mainNavbar");
  if (!navbar) return;

  const onScroll = () => {
    if (window.scrollY > 20) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  };

  // Set initial state and listen
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}


/* ================================================================
   2. Flash Messages – auto-dismiss after 5 seconds
   ================================================================ */
function initFlashAutoDismiss() {
  const alerts = document.querySelectorAll(".vx-alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      // Bootstrap's dismiss API with safe fallback
      if (typeof bootstrap !== "undefined") {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } else {
        // Fallback: fade out and remove natively
        alert.style.transition = "opacity 0.5s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
      }
    }, 5000);
  });
}


/* ================================================================
   3. Active nav-link – highlight based on current URL path
      (Jinja already sets the "active" class server-side, but this
       acts as a client-side fallback / enhancement)
   ================================================================ */
function initActiveNavLink() {
  const currentPath = window.location.pathname;
  const navLinks    = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach((link) => {
    // Exact match for home; prefix match for other pages
    const href = link.getAttribute("href");
    if (!href) return;
    if (href === currentPath || (href !== "/" && currentPath.startsWith(href))) {
      link.classList.add("active");
    }
  });
}


/* ================================================================
   4. Fade-in stagger for feature / stat cards
      Adds a tiny delay per card for a cascading entrance effect.
   ================================================================ */
function initFadeInCards() {
  const cards = document.querySelectorAll(
    ".vx-feature-card, .vx-stat-card, .vx-card"
  );

  if (!("IntersectionObserver" in window)) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          // Stagger each card by 80ms
          entry.target.style.animationDelay = `${i * 80}ms`;
          entry.target.classList.add("vx-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  cards.forEach((card) => observer.observe(card));
}
