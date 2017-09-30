var loadConditionForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: {"dst": btn.attr("data-dst")},
      beforeSend: function() {
        $("#modal-item").modal("show");
      },
      success: function(data) {
        $("#modal-item .modal-content").html(data.html_form);
        $('input#id_formula').hide();
        id_formula_value = $('input#id_formula').val();
        if (id_formula_value != "") {
          options['rules'] = JSON.parse(id_formula_value);
        }
        $('#builder').queryBuilder(options);
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
    $('input#id_formula').val(f_text);
    payload = form.serialize();
    $.ajax({
      url: form.attr("action"),
      data: payload,
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          if (data.dst == 'refresh') {
            $("#item-table tbody").html(data.html_item_list);
            $("#modal-item").modal("hide");
          }
          else {
            location.href = data.html_redirect;
          }
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
          $('input#id_formula').hide();
          id_formula_value = $('input#id_formula').val();
          if (id_formula_value != "") {
            options['rules'] = JSON.parse(id_formula_value);
          }
          $('#builder').queryBuilder(options);
        }
      }
    });
    return false;
};

var insertConditionInContent = function() {
  var btn = $(this);
  insert_text = "{% if " + btn.attr('data-name') +
      " %}YOUR TEXT HERE{% endif %}";
  tinyMCE.activeEditor.execCommand('mceInsertContent', false, insert_text);
};

var insertAttributeInContent = function() {
  var val = $(this).val();
  if (val == '') {
    return;
  }
  insert_text = "{{ " + val + " }}";
  tinyMCE.activeEditor.execCommand('mceInsertContent', false, insert_text);
  $(this).val("");
}

$(function () {
  // Create Action
  $(".js-create-action").click(loadForm);
  $("#modal-item").on("submit", ".js-action-create-form", saveForm);

  // Update Action
  // $("#action-table").on("click", ".js-update-action", loadForm);
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

  // Preview
  $("#html-editor").on("click", ".js-action-preview", loadForm);
  $(".modal-content").on("click", ".js-action-preview-nxt", loadForm);
  $(".modal-content").on("click", ".js-action-preview-prv", loadForm);
});
