// ==========================================================================
// File : static/js/documents.js
// What : Document upload rows (Add candidate form and Candidate details page)
//        - "+ Add another document" adds a new row (type + name + file)
//        - "Remove" removes a row
//        - checks file type and size in the browser before sending
//        (the server checks again, so this is only for convenience)
//        - asks "are you sure?" before deleting a document
// ==========================================================================

//-------------- Start Code for Document upload rows -----------------
(function () {
  "use strict";

  document.querySelectorAll("[data-doc-rows]").forEach(function (box) {
    var template = box.querySelector("template[data-doc-template]");
    var addButton = box.querySelector("[data-doc-add]");
    var maxFiles = parseInt(box.getAttribute("data-max-files"), 10) || 10;
    var maxBytes = (parseFloat(box.getAttribute("data-max-mb")) || 10) * 1024 * 1024;
    var allowed = box.getAttribute("data-accept").toLowerCase().split(",");
    var nextIndex = 1;                      // row 0 is already on the page

    function rows() { return box.querySelectorAll("[data-doc-row]"); }

    // "Remove" is shown only when there is more than one row.
    function refresh() {
      var all = rows();
      all.forEach(function (row) { row.querySelector("[data-doc-remove]").hidden = all.length < 2; });
      addButton.disabled = all.length >= maxFiles;
      addButton.title = addButton.disabled ? "At most " + maxFiles + " documents at a time" : "";
    }

    addButton.hidden = false;               // shown only when JavaScript works

    addButton.addEventListener("click", function () {
      if (rows().length >= maxFiles) { return; }
      var holder = document.createElement("div");
      holder.innerHTML = template.innerHTML.split("__I__").join(String(nextIndex++));
      var row = holder.firstElementChild;
      box.insertBefore(row, addButton);
      refresh();
      row.querySelector("select").focus();
    });

    box.addEventListener("click", function (event) {
      var remove = event.target.closest("[data-doc-remove]");
      if (!remove) { return; }
      remove.closest("[data-doc-row]").remove();
      refresh();
    });

    // Check a chosen file: allowed type and size.
    box.addEventListener("change", function (event) {
      var input = event.target;
      if (!input.matches("[data-doc-file]")) { return; }
      var message = input.closest("[data-doc-row]").querySelector(".doc-row__error");
      message.textContent = "";
      var file = input.files && input.files[0];
      if (!file) { return; }

      var dot = file.name.lastIndexOf(".");
      var ext = dot >= 0 ? file.name.slice(dot).toLowerCase() : "";
      if (allowed.indexOf(ext) === -1) {
        message.textContent = "\u201c" + file.name + "\u201d is not allowed. Choose a PDF, image or Word file.";
        input.value = "";
      } else if (file.size > maxBytes) {
        message.textContent = "\u201c" + file.name + "\u201d is larger than " + (maxBytes / 1048576) + " MB.";
        input.value = "";
      } else if (file.size === 0) {
        message.textContent = "\u201c" + file.name + "\u201d is empty.";
        input.value = "";
      }
    });

    refresh();
  });

  // Delete buttons: ask first.
  document.addEventListener("submit", function (event) {
    var question = event.target.getAttribute && event.target.getAttribute("data-confirm");
    if (question && !window.confirm(question)) { event.preventDefault(); }
  });
})();
//-------------- End of the code ------------------------------
