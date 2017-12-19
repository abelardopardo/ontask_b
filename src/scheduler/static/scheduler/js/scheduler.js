$(function () {
  // Delete scheduled action
  $(".js-scheduleremail-delete").click(loadForm);
  $("#modal-item").on("submit", ".js-scheduleremail-delete-form", saveForm);
});