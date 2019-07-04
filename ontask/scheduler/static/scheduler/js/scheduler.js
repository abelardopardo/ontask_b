$(function () {
  // View scheduled action
  $(".js-scheduler-view").click(loadForm);
  $("#modal-item").on("click", ".js-scheduler-view", loadForm);

  // Delete scheduled action
  $(".js-scheduler-delete").click(loadForm);
  $("#modal-item").on("submit", ".js-scheduler-delete-form", saveForm);
  if (document.getElementById("id_confirm_items") != null) {
    $("#id_confirm_items").on("change", function(e) {
      select_next_button($(this));
    })
  } else {
    $("#id_item_column").on("change", function(e) {
      select_next_button($(this));
    })
  }
});
$(document).ready(function() {
  if (document.getElementById("id_confirm_items") != null) {
    select_next_button($("#id_confirm_items"));
  } else {
    select_next_button($("#id_item_column"));
  }
});
window.onload = function(){
  setDateTimePickers();
};
