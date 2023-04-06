let conditionClone = function() {
  $("#div-spinner").show();
  $.ajax({
    url: $(this).attr("data-url"),
    data: {"action_content": get_id_text_content(), "csrfmiddlewaretoken": window.CSRF_TOKEN},
    type: "post",
    dataType: "json",
    success: function (data) {
      if (typeof data.html_redirect != "undefined") {
        if (data.html_redirect == "") {
          location.reload(true);
        } else {
          location.href = data.html_redirect;
        }
        return;
      }
      $("#div-spinner").hide();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      location.reload(true);
    },
  });
}
let transferFormula = function () {
  if (document.getElementById("id__formula") != null) {
    let formula = $("#builder").queryBuilder('getRules');
    if (formula == null || !formula['valid']) {
      $('#div-spinner').hide();
      return false;
    }
    let f_text = JSON.stringify(formula, undefined, 2);
    $("#id__formula").val(f_text);
   }
   return true;
}
$(function () {
  // Create Condition
  $("#condition-set-header").on("click", ".js-condition-create", loadForm);
  $("#modal-item").on("submit", ".js-condition-create-form", saveForm);

  // Edit Condition
  $("#condition-set").on("click", ".js-condition-edit", loadForm);
  $("#modal-item").on("submit", ".js-condition-edit-form", saveForm);

  // Clone Condition
  $("#condition-set").on("click", ".js-condition-clone", conditionClone);
  $("#condition-clone").on("click", ".js-condition-clone", conditionClone);

  // Delete Condition
  $("#condition-set").on("click", ".js-condition-delete", loadForm);
  $("#modal-item").on("submit", ".js-condition-delete-form", saveForm);

  // Create filter
  $("#filter-set-header").on("click", ".js-filter-create", loadForm);
  $("#modal-item").on("submit", ".js-filter-create-form", saveForm);

  // Edit Filter
  $("#filter-set").on("click", ".js-filter-edit", loadForm);
  $("#modal-item").on("submit", ".js-filter-edit-form", saveForm);

  // Update Filter
  $("#filter").on("submit", ".js-filter-update-form", transferFormula);

  // Delete Filter
  $("#filter").on("click", ".js-filter-delete", loadForm);
  $("#modal-item").on("submit", ".js-filter-delete-form", saveForm);
})
