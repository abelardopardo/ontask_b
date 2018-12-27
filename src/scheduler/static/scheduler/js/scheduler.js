$(function () {
  // View scheduled action
  $(".js-scheduler-view").click(loadForm);
  $("#modal-item").on("click", ".js-scheduler-view", loadForm);

  // Delete scheduled action
  $(".js-scheduler-delete").click(loadForm);
  $("#modal-item").on("submit", ".js-scheduler-delete-form", saveForm);
});
window.onload = function(){
  setDateTimePickers();
};
