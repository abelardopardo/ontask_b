$(function () {
  // Connection add, edit, delete and clone
  $("#connection-admin").on("click", ".js-connection-view", loadForm);
  $("#connection-instructor").on("click", ".js-connection-view", loadForm);
  $("#connection-admin").on("click", ".js-connection-addedit", loadForm);
  $("#modal-item").on("submit", ".js-connection-addedit-form", saveForm);
  $("#connection-admin, #modal-item").on("click", ".js-connection-delete", loadForm);
  $("#modal-item").on("submit", ".js-connection-delete-form", saveForm);
  $("#connection-admin, #modal-item").on("click", ".js-connection-clone", loadForm);
  $("#modal-item").on("submit", ".js-connection-clone-form", saveForm);

  // Toggle enable connections
  $("#connection-admin-table").on("change", ".toggle-checkbox", toggleCheckBox);
});
