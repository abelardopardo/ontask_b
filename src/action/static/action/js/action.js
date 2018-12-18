function insertAtCaret(areaId, text) {
    var txtarea = document.getElementById(areaId);
    var scrollPos = txtarea.scrollTop;
    var caretPos = txtarea.selectionStart;

    var front = (txtarea.value).substring(0, caretPos);
    var back = (txtarea.value).substring(txtarea.selectionEnd, txtarea.value.length);
    txtarea.value = front + text + back;
    caretPos = caretPos + text.length;
    txtarea.selectionStart = caretPos;
    txtarea.selectionEnd = caretPos;
    txtarea.focus();
    txtarea.scrollTop = scrollPos;
}
var insertText = function(areaId, insert_text) {
  if (typeof $('#' + areaId).summernote != 'undefined') {
    $('#' + areaId).summernote('editor.insertText', insert_text);
  } else {
    insertAtCaret(areaId, insert_text);
  }

}
var insertConditionInContent = function() {
  var btn = $(this);
  if (typeof $('#id_content').summernote != 'undefined') {
    var range = $("#id_content").summernote('createRange');
    condition_text = gettext('YOUR TEXT HERE');
    range_text = range.toString();
    if (range_text != '') {
      condition_text = range_text;
    }
  } else {
      condition_text = '';
  }
  insert_text = "{% if " + btn.val() +
      " %}" + condition_text + "{% endif %}";
  insertText('id_content', insert_text);
  $(this).val(this.defaultSelected);
};
var insertAttributeInContent = function() {
  var val = $(this).val();
  if (val == '') {
    return;
  }
  insertText('id_content', "{{ " + val + " }}");
  $(this).val(this.defaultSelected);
}
var insertColumnInActionIn = function () {
  var val = $(this).val();
  var sel = $(this)
  $('#div-spinner').show();
  //window.location = val;
  $.ajax({
    url: val,
    type: 'get',
    dataType: 'json',
    success: function (data) {
      if (typeof data.html_redirect != 'undefined') {
        location.href = data.html_redirect;
      } else {
        $('#div-spinner').hide();
      }
      sel.children("option[value='']").remove();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      location.reload(true);
    }
  });
}
var toggleShuffleQuestion = function () {
  $('#div-spinner').show();
  $.ajax({
    url: $(this).attr("data-url"),
    type: 'get',
    dataType: 'json',
    success: function (data) {
        if (data.shuffle = true) {
            $(this).attr('checked')
        } else {
            $(this).removeAttr('checked')
        }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $('#div-spinner').show();
      location.reload(true);
    }
  });
  $('#div-spinner').hide();
}
var loadFormPost = function () {
    var btn = $(this);
    if ($(this).is('[class*="disabled"]')) {
      return;
    }
    $.ajax({
      url: $(this).attr("data-url"),
      data: [{'name': 'action_content', 'value': get_id_content()}],
      type: 'post',
      dataType: 'json',
      beforeSend: function() {
        $(".modal-body").html("");
        $("#modal-item").modal("show");
      },
      success: function(data) {
        if (data.form_is_valid) {
          if (data.html_redirect == "") {
            $('#div-spinner').show();
            window.location.reload(true);
          } else {
            location.href = data.html_redirect;
          }
          return;
        }
        $("#modal-item .modal-content").html(data.html_form);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $('#div-spinner').show();
        location.reload(true);
      }
    });
}
var transferFormula = function () {
  if (document.getElementById("id_filter_formula") != null) {
    formula = $("#filter_builder").queryBuilder('getRules');
    if (formula == null || !formula['valid']) {
      $('#div-spinner').hide();
      return false;
    }
    f_text = JSON.stringify(formula, undefined, 2);
    $("#id_filter_formula").val(f_text);
   }
   return true;
}
var conditionClone = function() {
  $('#div-spinner').show();
  $.ajax({
    url: $(this).attr("data-url"),
    data: [{'name': 'action_content', 'value': get_id_content()}],
    type: 'post',
    dataType: 'json',
    success: function (data) {
      if (typeof data.html_redirect != 'undefined') {
        if (data.html_redirect == '') {
          location.reload(true);
        } else {
          location.href = data.html_redirect;
        }
      } else {
        $('#div-spinner').hide();
      }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      location.reload(true);
    },
  });
}
$(function () {
  $("#checkAll").click(function () {
       $("input[id*='id_upload_']").prop("checked", this.checked);
  });

  // Create Action
  $(".js-create-action").click(loadForm);
  $("#modal-item").on("submit", ".js-action-create-form", saveForm);

  // Edit Action
  $("#action-table").on("click", ".js-action-update", loadForm);
  $("#modal-item").on("submit", ".js-action-update-form", saveForm);

  // Delete Action
  $("#action-table").on("click", ".js-action-delete", loadForm);
  $("#modal-item").on("submit", ".js-action-delete-form", saveForm);

  // Clone Action
  $("#action-table").on("click", ".js-action-clone", loadForm);
  $("#modal-item").on("submit", ".js-action-clone-form", saveForm);

  // Edit Action Description
  $("#action-in-editor").on("click", ".js-description-edit", loadForm);
  $("#modal-item").on("submit", ".js-description-edit-form", saveForm);

  // Update Filter
  $("#filter").on("submit", ".js-filter-update-form", transferFormula);

  // Delete Filter
  $("#filter").on("click", ".js-filter-delete", loadForm);
  $("#modal-item").on("submit", ".js-filter-delete-form", saveForm);

  // Create Condition
  $("#condition-set-header").on("click", ".js-condition-create", loadForm);
  $("#modal-item").on("submit", ".js-condition-create-form", saveForm);

  // Edit Condition
  $("#condition-set").on("click", ".js-condition-edit", loadForm);
  $("#modal-item").on("submit", ".js-condition-edit-form", saveForm);

  // Clone Condition
  $("#condition-set").on("click", ".js-condition-clone", conditionClone);

  // Delete Condition
  $("#condition-set").on("click", ".js-condition-delete", loadForm);
  $("#modal-item").on("submit", ".js-condition-delete-form", saveForm);

  // Insert condition blurb in the editor
  $("#attribute-names").on("change",
                           "#select-condition-name",
                           insertConditionInContent);
//  $("#condition-set").on("click", ".js-condition-insert",
//    insertConditionInContent);

  // Insert attribute in content
  $("#attribute-names").on("change",
                           "#select-attribute-name",
                           insertAttributeInContent);
  // Insert attribute column in content
  $("#attribute-names").on("change",
                           "#select-column-name",
                           insertAttributeInContent);

  // Insert columns in action in
  $("#questions").on("change",
                      "#select-column-name",
                      insertColumnInActionIn);

  // Insert columns in action in
  $("#parameters").on("change",
                      "#select-key-column-name",
                      insertColumnInActionIn);

  // Toggle shuffle question
  $("#action-in-editor").on("change",
                       "#shuffle-questions",
                       toggleShuffleQuestion);

  // Preview
  $("#action-preview-done").on("click", ".js-action-preview", loadFormPost);
  $("#email-action-request-data").on("click", ".js-email-preview", loadForm);
  $("#canvas-email-action-request-data").on("click",
    ".js-canvas-email-preview",
    loadForm);
  $("#zip-action-request-data").on("click", ".js-zip-preview", loadForm);
  $("#json-action-request-data").on("click", ".js-json-preview", loadForm);
  $("#action-in-editor").on("click", ".js-action-preview", loadForm);
  $(".modal-content").on("click", ".js-action-preview-nxt", loadForm);
  $(".modal-content").on("click", ".js-action-preview-prv", loadForm);

  // Show URL
  $("#action-table").on("click", ".js-action-showurl", loadForm);
  $("#modal-item").on("submit", ".js-action-showurl-form", saveForm);

  // Column Add
  $("#edit-survey-tab-content").on("click", ".js-workflow-question-add", loadForm);
  $("#modal-item").on("submit", ".js-workflow-question-add-form", saveForm);

  // Column Selected Edit
  $("#column-selected-table").on("click",
    ".js-workflow-question-edit",
    loadForm);
  $("#modal-item").on("submit", ".js-question-edit-form", saveForm);

  // Delete column
  $("#column-selected-table").on("click", ".js-column-delete", loadForm);
  $("#modal-item").on("submit", ".js-column-delete-form", saveForm);

  // Clone column
  $("#column-selected-table").on("click", ".js-column-clone", loadForm);
  $("#modal-item").on("submit", ".js-column-clone-form", saveForm);

  // Flush workflow in detail view
  $("#action-index").on("click", ".js-workflow-flush", loadForm);
  $("#modal-item").on("submit", ".js-workflow-flush-form", saveForm);
});

window.onload = function(){
  if (document.getElementById("id_exclude_values") != null) {
    set_element_select("#id_exclude_values");
  }
  setDateTimePickers();
  if (typeof qbuilder_filter_options != "undefined") {
    if ($('#id_filter_formula').val() != '') {
      qbuilder_filter_options["rules"] = JSON.parse($('#id_filter_formula').val());
    }
    $("#filter_builder").queryBuilder(qbuilder_filter_options);
  }
};

