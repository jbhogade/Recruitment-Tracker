// ==========================================================================
// File : static/js/option_adder.js
// What : The (+) button on the Add candidate form.
//        Press (+) beside Education / Department / Position / Source /
//        Interviewer, type the missing value, press Add. The value is saved
//        on the server, added to the dropdown and selected - no page change.
//        Also shows the "Referred by (employee)" field only when
//        Reference / Source = Employee Referral.
// ==========================================================================

//-------------- Start Code for (+) add-new-choice buttons -----------------
(function () {
  "use strict";

  var form = document.querySelector("form[data-option-url]");
  if (!form) { return; }

  var url = form.getAttribute("data-option-url");
  var token = (form.querySelector("[name=csrfmiddlewaretoken]") || {}).value || "";

  // Set up every dropdown field that has a (+) button.
  form.querySelectorAll("[data-option-field]").forEach(function (box) {
    var field = box.getAttribute("data-option-field");
    var select = box.querySelector("select");
    var plus = box.querySelector("[data-add-option]");
    var panel = box.querySelector(".add-box");
    var input = panel.querySelector(".add-box__input");
    var message = panel.querySelector(".add-box__msg");
    var status = box.querySelector(".field__status");
    var saveButton = panel.querySelector("[data-add-save]");
    var busy = false;

    plus.hidden = false;      // the button is hidden in the HTML and shown only when JavaScript works

    // ---- open / close the small add box ----
    function openBox() {
      panel.hidden = false;
      plus.setAttribute("aria-expanded", "true");
      message.textContent = "";
      input.value = "";
      input.focus();
    }
    function closeBox() {
      panel.hidden = true;
      plus.setAttribute("aria-expanded", "false");
      message.textContent = "";
      plus.focus();
    }
    plus.addEventListener("click", function () { if (panel.hidden) { openBox(); } else { closeBox(); } });
    panel.querySelector("[data-add-cancel]").addEventListener("click", closeBox);

    // ---- put the new value into the dropdown (alphabetical) and select it ----
    function selectValue(value) {
      var found = null;
      Array.prototype.forEach.call(select.options, function (opt) { if (opt.value === value) { found = opt; } });
      if (!found) {
        found = new Option(value, value);
        var placed = false;
        for (var i = 1; i < select.options.length; i++) {     // option 0 is the blank choice
          if (select.options[i].value.toLowerCase() > value.toLowerCase()) {
            select.add(found, select.options[i]);
            placed = true;
            break;
          }
        }
        if (!placed) { select.add(found); }
      }
      select.value = value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // ---- save the new value on the server ----
    function save() {
      if (busy) { return; }
      var typed = input.value.trim();
      if (!typed) { message.textContent = "Type the new value first."; input.focus(); return; }

      busy = true;
      saveButton.disabled = true;
      message.textContent = "";
      var data = new FormData();
      data.append("field", field);
      data.append("value", typed);

      fetch(url, { method: "POST", body: data, headers: { "X-CSRFToken": token }, credentials: "same-origin" })
        .then(function (response) { return response.json().then(function (json) { return { ok: response.ok, json: json }; }); })
        .then(function (result) {
          if (!result.ok || !result.json.ok) {
            message.textContent = (result.json && result.json.error) || "Could not save. Please try again.";
            return;
          }
          selectValue(result.json.value);
          status.textContent = result.json.existing
            ? "\u201c" + result.json.value + "\u201d is already in the list. It has been selected."
            : "\u201c" + result.json.value + "\u201d added to the list and selected.";
          closeBox();
        })
        .catch(function () { message.textContent = "Could not reach the server. Please try again."; })
        .then(function () { busy = false; saveButton.disabled = false; });
    }
    saveButton.addEventListener("click", save);

    // Enter inside the box adds the value (and must NOT submit the whole form); Escape closes the box.
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") { event.preventDefault(); save(); }
      else if (event.key === "Escape") { event.preventDefault(); closeBox(); }
    });

    // Choosing something in the dropdown clears the old "added" message.
    select.addEventListener("change", function () { if (!busy) { status.textContent = ""; } });
  });
})();
//-------------- End of the code ------------------------------


//-------------- Start Code for "Referred by" field (only for Employee Referral) -----------------
(function () {
  "use strict";

  var wrapper = document.querySelector("[data-referral-field]");
  var source = document.getElementById("id_source");
  if (!wrapper || !source) { return; }

  var referralValue = wrapper.getAttribute("data-referral-field");   // "Employee Referral"
  var referrer = wrapper.querySelector("select");
  var addBox = wrapper.querySelector(".add-box");

  function update() {
    var isReferral = source.value === referralValue;
    wrapper.hidden = !isReferral;
    if (!isReferral) {                       // not a referral: forget any earlier choice
      referrer.value = "";
      if (addBox) { addBox.hidden = true; }
    }
  }

  source.addEventListener("change", update);
  update();
})();
//-------------- End of the code ------------------------------

