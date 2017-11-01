var loadConditionForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: {'action_content': $("#id_content").summernote('code')},
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
        $('#id_formula').hide();
        id_formula_value = $('#id_formula').val();
        if (id_formula_value != "null" && id_formula_value != "{}") {
          qbuilder_options['rules'] = JSON.parse(id_formula_value);
        }
        $('#builder').queryBuilder(qbuilder_options);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
}

var saveConditionForm = function () {
    var form = $(this);
    formula = $('#builder').queryBuilder('getRules');
    if (formula == null || !formula['valid']) {
      return false;
    }
    f_text = JSON.stringify(formula, undefined, 2);
    $('#id_formula').val(f_text);
    // $('#id_formula').val(formula);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          location.href = data.html_redirect;
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
          $('#id_formula').hide();
          id_formula_value = $('#id_formula').val();
          if (id_formula_value != "null" && id_formula_value != {}) {
            qbuilder_options['rules'] = JSON.parse(id_formula_value);
          }
          $('#builder').queryBuilder(qbuilder_options);
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
    return false;
};

var insertConditionInContent = function() {
  var btn = $(this);
  var range = $("#id_content").summernote('createRange');
  condition_text = 'YOUR TEXT HERE';
  range_text = range.toString();
  if (range_text != '') {
    condition_text = range_text;
  }
  insert_text = "{% if " + btn.attr('data-name') +
      " %}" + condition_text + "{% endif %}";
  $('#id_content').summernote('editor.insertText', insert_text);
};

var insertAttributeInContent = function() {
  var val = $(this).val();
  if (val == '') {
    return;
  }
  insert_text = "{{ " + val + " }}";
  $('#id_content').summernote('editor.insertText', insert_text);
}

$(function () {
  // Create Action
  $(".js-create-action").click(loadForm);
  $("#modal-item").on("submit", ".js-action-create-form", saveForm);

  // Update Action
  $("#item-table").on("click", ".js-action-update", loadForm);
  $("#modal-item").on("submit", ".js-action-update-form", saveForm);

  // Delete Action
  $("#item-table").on("click", ".js-action-delete", loadForm);
  $("#modal-item").on("submit", ".js-action-delete-form", saveForm);

  // Create filter
  $("#filter-set").on("click", ".js-filter-create", loadConditionForm);
  $("#modal-item").on("submit", ".js-filter-create-form", saveConditionForm);

  // Edit Filter
  $("#filter-set").on("click", ".js-filter-edit", loadConditionForm);
  $("#modal-item").on("submit", ".js-filter-edit-form", saveConditionForm);

  // Delete Filter
  $("#filter-set").on("click", ".js-filter-delete", loadForm);
  $("#modal-item").on("submit", ".js-filter-delete-form", saveForm);

  // Create Condition
  $("#condition-set").on("click", ".js-condition-create", loadConditionForm);
  $("#modal-item").on("submit", ".js-condition-create-form", saveConditionForm);

  // Edit Condition
  $("#condition-set").on("click", ".js-condition-edit", loadConditionForm);
  $("#modal-item").on("submit", ".js-condition-edit-form", saveConditionForm);

  // Delete Condition
  $("#condition-set").on("click", ".js-condition-delete", loadForm);
  $("#modal-item").on("submit", ".js-condition-delete-form", saveForm);

  // Insert condition blurb in the editor
  $("#condition-set").on("click", ".js-condition-insert",
    insertConditionInContent);

  // Insert attribute in content
  $("#attribute-names").on("change",
                           "#select-attribute-name",
                           insertAttributeInContent);
  $("#attribute-names").on("change",
                           "#select-column-name",
                           insertAttributeInContent);

  // Preview
  $("#html-editor").on("click", ".js-action-preview", loadForm);
  $(".modal-content").on("click", ".js-action-preview-nxt", loadForm);
  $(".modal-content").on("click", ".js-action-preview-prv", loadForm);

  // Show URL
  $("#item-table").on("click", ".js-action-showurl", loadForm);
});

$(document).ready(function() {
    if (document.getElementById("item-table") != null) {
        // Required for DataTables
        $('#item-table').DataTable({
            "language": {
                "emptyTable": "There are no actions for this workflow."
            },
            "columnDefs": [
                {"orderable": false, "targets": 3},
                {"searchable": false, "targets": 3},
            ],
        });
    }
    if (document.getElementById("id_content") != null) {
      initSummernote();
    }
});


