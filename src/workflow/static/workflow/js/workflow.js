$(function () {
  // Create Workflow
  $(".js-create-workflow").click(loadForm);
  $("#modal-item").on("submit", ".js-workflow-create-form", saveForm);

  // Update Workflow
  $("#item-table").on("click", ".js-workflow-update", loadForm);
  $("#modal-item").on("submit", ".js-workflow-update-form", saveForm);

  // Delete Workflow
  $("#item-table").on("click", ".js-workflow-delete", loadForm);
  $("#workflow-table").on("click", ".js-workflow-delete", loadForm);
  $("#modal-item").on("submit", ".js-workflow-delete-form", saveForm);

  // Flush workflow in detail view
  $("#workflow-table").on("click", ".js-workflow-flush", loadForm);
  $("#modal-item").on("submit", ".js-workflow-flush-form", saveForm)

  // Add attribute
  $("#workflow-attributes").on("click", ".js-attribute-create", loadForm);
  $("#modal-item").on("submit", ".js-attribute-create-form", saveForm)

  // Delete attribute
  $("#attribute-table").on("click", ".js-attribute-delete", loadForm)
  $("#modal-item").on("submit", ".js-attribute-delete-form", saveForm)
});
