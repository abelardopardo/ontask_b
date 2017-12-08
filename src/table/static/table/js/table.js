$(function () {
  // Column Add
  $("#table-content").on("click", ".js-workflow-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-add-form", saveForm);

  // Column Edit
  $("#table-data").on("click", ".js-workflow-column-edit", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-edit-form", saveForm);

  // Row delete
  $("#table-content").on("click", ".js-row-delete", loadForm);
  $("#modal-item").on("submit", ".js-row-delete-form", saveForm);
});
