var table_filter = '{}';
var table_data;
var loadFilter = function() {
    if (table_filter != "null" && table_filter != "{}") {
      qbuilder_options['rules'] = JSON.parse(table_filter);
    }
    $('#builder').queryBuilder(qbuilder_options);
    $("#modal-item").modal('show');
}
var saveFilter = function() {
    var div_content = $(this);
    formula = $('#builder').queryBuilder('getRules', {'skip_empty': true});
    if (formula == null || !formula['valid']) {
      return false;
    }
    f_text = JSON.stringify(formula, undefined, 2);
    table_filter = f_text;
    $("#modal-item").modal('hide');
    table_data.ajax.reload();
    if (formula['rules'].length == 0) {
      $('#badge_text').text('off');
    } else {
      $('#badge_text').text('on');
    }
}
$(function () {
  // Column Add
  $("#table-content").on("click", ".js-workflow-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-add-form", saveForm);

  // Derived column add
  $("#table-content").on("click", ".js-workflow-formula-column-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-formula-column-add-form",
  saveForm);

  // Column Edit
  $("#table-data").on("click", ".js-workflow-column-edit", loadForm);
  $("#modal-item").on("submit", ".js-workflow-column-edit-form", saveForm);

  // Row delete
  $("#table-content").on("click", ".js-row-delete", loadForm);
  $("#modal-item").on("submit", ".js-row-delete-form", saveForm);

  // Filter Edit
  $("#table-content").on("click", ".js-table-filter-edit", loadFilter);
  $("#modal-item").on("click", ".js-table-filter-edit-form", saveFilter);
});
