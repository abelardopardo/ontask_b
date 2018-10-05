$(function () {
  // Column Add
  $("#table-content").on("click", ".js-workflow-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-add-form", saveForm);

  // Derived column add
  $("#table-content").on("click", ".js-workflow-formula-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-formula-column-add-form",
  saveForm);

  // Column Edit
  $("#table-data").on("click", ".js-column-edit", loadForm);
  $("#modal-item").on("submit", ".js-column-edit-form", saveForm);

  // Delete column
  $("#table-data").on("click", ".js-column-delete", loadForm)
  $("#modal-item").on("submit", ".js-column-delete-form", saveForm)

  // Clone column
  $("#table-data").on("click", ".js-column-clone", loadForm);
  $("#modal-item").on("submit", ".js-column-clone-form", saveForm);

  // Row delete
  $("#table-content").on("click", ".js-row-delete", loadForm);
  $("#modal-item").on("submit", ".js-row-delete-form", saveForm);

  // View add
  $("#view-content").on("click", ".js-view-add", loadForm);
  $("#modal-item").on("submit", ".js-view-add-form", saveForm);

  // View edit (both in view index and display pages)
  $("#view-content").on("click", ".js-view-edit", loadForm);
  $("#table-content").on("click", ".js-view-edit", loadForm);
  $("#modal-item").on("click", ".js-view-edit-form", saveForm);

  // View delete
  $("#view-content").on("click", ".js-view-delete", loadForm);
  $("#modal-item").on("submit", ".js-view-delete-form", saveForm);

  // View clone
  $("#view-content").on("click", ".js-view-clone", loadForm);
  $("#modal-item").on("click", ".js-view-clone-form", saveForm);
});
window.onload = function(){
  setDateTimePickers();
};
