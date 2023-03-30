$(function () {
  $(".js-create-action").click(loadForm);
  $("#modal-item").on("submit", ".js-action-create-form", saveForm);

  $("#table-content").on("click", ".js-workflow-column-add", loadForm);
  // Column Add
  $("#modal-item").on("submit", ".js-workflow-column-add-form", saveForm);

  // Derived column add
  $("#table-content").on("click", ".js-workflow-formula-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-formula-column-add-form",
  saveForm);

  // Random column add
  $("#table-content").on("click", ".js-workflow-random-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-random-column-add-form",
  saveForm);

  // Show stats
  $("#column-stat-selector").on("click", ".js-show-stats", loadForm);

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
  $("#table-content").on("click", ".js-view-add", loadForm);
  $("#modal-item").on("submit", ".js-view-add-form", saveForm);

  // View edit (both in view index and display pages)
  $("#table-content").on("click", ".js-view-edit", loadForm);
  $("#modal-item").on("click", ".js-view-edit-form", saveForm);

  // View delete
  $("#table-content").on("click", ".js-view-delete", loadForm);
  $("#modal-item").on("submit", ".js-view-delete-form", saveForm);

  // View clone
  $("#table-content").on("click", ".js-view-clone", loadForm);
  $("#modal-item").on("click", ".js-view-clone-form", saveForm);

});
window.onload = function(){
  setDateTimePickers();
};
