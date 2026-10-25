// ==========================================================================
// File : static/js/theme.js
// What : Theme switcher. Remembers the chosen theme in the browser
//        (localStorage) so it stays after refresh or the next visit.
// ==========================================================================

//-------------- Start Code for Theme switcher -----------------
(function () {
  "use strict";

  var STORAGE_KEY = "rt_theme";   // name under which the choice is saved
  var DEFAULT_THEME = "dark";
  var root = document.documentElement;
  var buttons = document.querySelectorAll("[data-theme-choice]");

  // Highlight the button of the active theme (and tell screen readers).
  function markActive(theme) {
    buttons.forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-theme-choice") === theme ? "true" : "false");
    });
  }

  // Apply a theme and save it.
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    markActive(theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) { /* storage blocked: ignore */ }
  }

  // When the page opens, show the current theme as selected.
  markActive(root.getAttribute("data-theme") || DEFAULT_THEME);

  // Click on a circle = switch theme.
  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      applyTheme(btn.getAttribute("data-theme-choice"));
    });
  });
})();
//-------------- End of the code ------------------------------
