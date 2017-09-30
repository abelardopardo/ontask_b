$(function () {
  // Preview
  $("#email-action-request-data").on("click", ".js-email-preview", loadForm);
  $(".modal-content").on("click", ".js-action-preview-nxt", loadForm);
  $(".modal-content").on("click", ".js-action-preview-prv", loadForm);
});
