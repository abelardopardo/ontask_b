function insertAtCaret(areaId, text) {
    let txtarea = document.getElementById(areaId);
    let scrollPos = txtarea.scrollTop;
    let caretPos = txtarea.selectionStart;
    let front = (txtarea.value).substring(0, caretPos);
    let back = (txtarea.value).substring(txtarea.selectionEnd, txtarea.value.length);
    txtarea.value = front + text + back;
    caretPos = caretPos + text.length;
    txtarea.selectionStart = caretPos;
    txtarea.selectionEnd = caretPos;
    txtarea.focus();
    txtarea.scrollTop = scrollPos;
}
let insertText = function(areaId, insert_text) {
  if (typeof $('#' + areaId).summernote != 'undefined') {
    $('#' + areaId).summernote('editor.insertText', insert_text);
  } else {
    insertAtCaret(areaId, insert_text);
  }
}
let insertConditionInContent = function() {
  let btn = $(this);
  let condition_text = ''
  if (typeof $('#id_text_content').summernote != 'undefined') {
    let range = $("#id_text_content").summernote('createRange');
    let range_text = range.toString();
    condition_text = gettext('YOUR TEXT HERE');
    if (range_text != '') {
      condition_text = range_text;
    }
  } else {
      condition_text = '';
  }
  let insert_text = "{% if " + btn.text() +
      " %}" + condition_text + "{% endif %}";
  insertText('id_text_content', insert_text);
  $(this).val(this.defaultSelected);
};
let insertAttributeInContent = function() {
  let val = $(this).text();
  if (val == '') {
    return;
  }
  if (typeof $('#id_text_content').summernote != 'undefined') {
    $("#id_text_content").summernote('createRange');
  }
  insertText('id_text_content', "{{ " + val + " }}");
  $(this).val(this.defaultSelected);
}
let ajax_post = function(url, data, req_type) {
  $.ajax({
    url: url,
    data: data,
    type: req_type,
    dataType: 'json',
    beforeSend: function() {
      $(".modal-body").html("");
      $("#modal-item").modal("show");
    },
    success: function(data) {
      if (typeof data.html_redirect != 'undefined') {
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
let loadFormPost = function () {
  let btn = $(this);
  if ($(this).is('[class*="disabled"]')) {
    return;
  }
  ajax_post(
    $(this).attr("data-url"),
    [{'name': 'action_content', 'value': get_id_text_content()}],
    'post'
  );
}
let transferFormula = function () {
  if (document.getElementById("id_formula") != null) {
    let formula = $("#builder").queryBuilder('getRules');
    if (formula == null || !formula['valid']) {
      $('#div-spinner').hide();
      return false;
    }
    let f_text = JSON.stringify(formula, undefined, 2);
    $("#id_formula").val(f_text);
   }
   return true;
}
let conditionClone = function() {
  $('#div-spinner').show();
  $.ajax({
    url: $(this).attr("data-url"),
    data: [{'name': 'action_content', 'value': get_id_text_content()}],
    type: 'post',
    dataType: 'json',
    success: function (data) {
      if (typeof data.html_redirect != 'undefined') {
        if (data.html_redirect == '') {
          location.reload(true);
        } else {
          location.href = data.html_redirect;
        }
        return;
      }
      $('#div-spinner').hide();
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

  // Create filter
  $("#filter-set-header").on("click", ".js-filter-create", loadForm);
  $("#modal-item").on("submit", ".js-filter-create-form", saveForm);

  // Edit Filter
  $("#filter-set").on("click", ".js-filter-edit", loadForm);
  $("#modal-item").on("submit", ".js-filter-edit-form", saveForm);

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
  $("#condition-clone").on("click", ".js-condition-clone", conditionClone);

  // Delete Condition
  $("#condition-set").on("click", ".js-condition-delete", loadForm);
  $("#modal-item").on("submit", ".js-condition-delete-form", saveForm);

  // Insert attribute column in content
  $("#insert-elements-in-editor").on("click", ".js-insert-column-name", insertAttributeInContent);
  // Insert condition blurb in the editor
  $("#insert-elements-in-editor").on("click", ".js-insert-condition-name", insertConditionInContent);
  // Insert attribute in content
  $("#insert-elements-in-editor").on("click", ".js-insert-attribute-name", insertAttributeInContent);

  // Insert columns in action in
  $("#insert-questions").on("click", ".js-insert-question", assignColumn);

  // Insert columns in action in
  $("#edit-survey-tab-content").on("click", ".js-select-key-column-name", assignColumn);

  // Insert columns in action in
  $("#edit-survey-tab-content").on("click", ".js-select-condition", assignColumn);

  // Toggle shuffle question
  $("#action-in-editor").on("change", "#shuffle-questions", toggleCheckBox);

  // Show stats
  $("#column-stat-selector").on("click", ".js-show-stats", loadForm);

  // Preview
  $("#action-preview-done").on("click", ".js-action-preview", loadFormPost);
  $("#email-action-request-data").on("click", ".js-action-preview", loadForm);
  $("#canvas-email-action-request-data").on("click",
    ".js-action-preview",
    loadForm);
  $("#zip-action-request-data").on("click", ".js-action-preview", loadForm);
  $("#json-action-request-data").on("click", ".js-action-preview", loadForm);
  $("#action-in-editor").on("click", ".js-action-preview", loadForm);
  $("#email-schedule-send").on("click", ".js-action-preview", loadForm);
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

  $(".card").hover(function(){
    $(this).css("background-color", "lightgray");
  }, function(){
    $(this).css("background-color", "white");
  });
  $("#id_confirm_items").on("change", function(e) {
    select_next_button($(this));
  })
});
window.onload = function(){
  if (document.getElementById("id_exclude_values") != null) {
    set_element_select("#id_exclude_values");
  }
  setDateTimePickers();
};
$(document).ready(function() {
  if (location.hash) {
    $("a[href='" + location.hash + "']").tab("show");
  }
  $(document.body).on("click", "a[data-toggle]", function(event) {
    location.hash = this.getAttribute("href");
  });
  select_next_button($("#id_confirm_items"));
});
$(window).on("popstate", function() {
  let anchor = location.hash || $("a[data-toggle='tab']").first().attr("href");
  $("a[href='" + anchor + "']").tab("show");
});
