// ==========================================================================
// File : static/js/candidates.js
// What : Candidates page only.
//        1) Applies a filter as soon as a dropdown changes
//           (without JavaScript the "Apply" button still works).
//        2) Closes the Export / Template menus on outside click or Escape.
// ==========================================================================

//-------------- Start Code for Auto-apply dropdown filters -----------------
(function () {
  "use strict";

  var form = document.getElementById("filter-form");
  if (!form) { return; }

  // Export / Template menus: only one open at a time, close on outside click or Escape.
  var menus = document.querySelectorAll("details.menu");
  menus.forEach(function (menu) {
    menu.addEventListener("toggle", function () {
      if (menu.open) { menus.forEach(function (other) { if (other !== menu) { other.open = false; } }); }
    });
  });
  document.addEventListener("click", function (event) {
    menus.forEach(function (menu) { if (!menu.contains(event.target)) { menu.open = false; } });
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") { menus.forEach(function (menu) { menu.open = false; }); }
  });

  // Every dropdown marked data-autosubmit sends the form when changed.
  form.querySelectorAll("select[data-autosubmit]").forEach(function (select) {
    select.addEventListener("change", function () { form.requestSubmit(); });
  });

  // Keep the web address short: filters left on "All" / empty search are not sent.
  form.addEventListener("submit", function () {
    form.querySelectorAll("select, input[type='search']").forEach(function (field) {
      if (field.value === "") { field.disabled = true; }
    });
  });
})();
//-------------- End of the code ------------------------------
