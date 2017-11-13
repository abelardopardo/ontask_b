// Required for DataTables
if (document.getElementById("item-table") != null) {
    $(document).ready(function() {
        $('#item-table').DataTable({
            "order": [[0, "asc"]],
            "language": {
                "emptyTable": "No workflows available."
            }
        });
        $('#column-table').DataTable({
            "language": {
                "emptyTable": "No columns available."
            }
        });
    });
}

$(function () {
  // Create Workflow
  $(".js-create-workflow").click(loadForm);
  $("#modal-item").on("submit", ".js-workflow-create-form", saveForm);

  // Delete Workflow
  $("#item-table").on("click", ".js-workflow-delete", loadForm);
  $("#workflow-table").on("click", ".js-workflow-delete", loadForm);
  $("#modal-item").on("submit", ".js-workflow-delete-form", saveForm);

  // Update Workflow
  $("#workflow-table").on("click", ".js-workflow-update", loadForm);
  $("#modal-item").on("submit", ".js-workflow-update-form", saveForm);

  // Flush workflow in detail view
  $("#workflow-table").on("click", ".js-workflow-flush", loadForm);
  $("#modal-item").on("submit", ".js-workflow-flush-form", saveForm)

  // Add attribute
  $("#workflow-attributes").on("click", ".js-attribute-create", loadForm);
  $("#modal-item").on("submit", ".js-attribute-create-form", saveForm)

  // Delete attribute
  $("#attribute-table").on("click", ".js-attribute-delete", loadForm)
  $("#modal-item").on("submit", ".js-attribute-delete-form", saveForm)

  // Add Share
  $("#workflow-shared").on("click", ".js-share-create", loadForm);
  $("#modal-item").on("submit", ".js-share-create-form", saveForm)

  // Delete share
  $("#share-table").on("click", ".js-share-delete", loadForm)
  $("#modal-item").on("submit", ".js-share-delete-form", saveForm)

  // Column Add
  $("#workflow-table").on("click", ".js-workflow-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-add-form", saveForm);

  // Column Edit
  $("#column-table").on("click", ".js-workflow-column-edit", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-edit-form", saveForm);

  // Delete column
  $("#column-table").on("click", ".js-column-delete", loadForm)
  $("#modal-item").on("submit", ".js-column-delete-form", saveForm)
});

