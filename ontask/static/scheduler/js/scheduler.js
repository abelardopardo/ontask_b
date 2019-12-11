let handle_multiple_executions = function(element, speed = 100){
  if (element.is(':checked')) {
    $('#div_id_frequency').show(speed);
    $('#div_id_execute_until').show(speed);
    $('#div_id_multiple_executions').css('border-bottom', 'none');
    $('#hint_id_multiple_executions').hide();
  } else {
    $('#div_id_multiple_executions').css('border-bottom', 'solid 1px gray');
    $('#div_id_frequency').hide(speed);
    $('#div_id_execute_until').hide(speed);
    $('#hint_id_multiple_executions').show();
  }
};
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
  // Toggle shuffle question
  $("#div_id_multiple_executions").on(
    "change",
    "#id_multiple_executions",
    function(){ handle_multiple_executions($(this))});
  // Toggle enable scheduled
  $("#scheduler-index").on("change", ".toggle-checkbox", toggleCheckBox);
});
$(document).ready(function() {
  if (document.getElementById("id_confirm_items") != null) {
    select_next_button($("#id_confirm_items"));
  } else {
    select_next_button($("#id_item_column"));
  }
  handle_multiple_executions($('#id_multiple_executions'), 'fast');
});
window.onload = function(){
  setDateTimePickers();
};
