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
  if (typeof tinymce != 'undefined' && tinymce.get(areaId) != 'undefined') {
    tinymce.get(areaId).execCommand('mceInsertContent', false, insert_text);
  } else {
    insertAtCaret(areaId, insert_text);
  }
}
let insertConditionInContent = function() {
  let btn = $(this);
  let condition_text = ''
  if (typeof tinymce != 'undefined' && tinymce.get('id_text_content') != 'undefined') {
    let range_text = tinymce.get('id_text_content').selection.getContent();
    condition_text = gettext('YOUR TEXT HERE');
    if (range_text != '') {
      condition_text = range_text;
    }
  } else {
      textarea_el = document.getElementById('id_text_content');
      condition_text = textarea_el.value.substring(textarea_el.selectionStart, textarea_el.selectionEnd);
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
  insertText('id_text_content', "{{ " + val + " }}");
  $(this).val(this.defaultSelected);
}
let insertRubricTextInContent = function() {
  insertText('id_text_content', "{% ot_insert_rubric_feedback %}");
  $(this).val(this.defaultSelected);
}
let insertColumnListInContent = function() {
  let report_column_list = $('#id_columns').val();
  if (report_column_list == '') {
    return;
  }
  insertText(
    'id_text_content',
    '{% ot_insert_report "' + report_column_list.join('" "') + '" %}');
  $(".modal-body").html("");
  $("#modal-item").modal('hide');
}
let loadFormPost = function () {
  let btn = $(this);
  previousActiveElement = btn;
  if (btn.is("[class*='dropdown-item']")) {
    previousActiveElement =  btn.parent().siblings()[0];
  }
  if ($(this).is('[class*="disabled"]')) {
    return;
  }
  ajaxPost(
    $(this).attr("data-url"),
    {'action_content': get_id_text_content(), "csrfmiddlewaretoken": window.CSRF_TOKEN},
    'post');
}
$(function () {
  $("#checkAll").click(function () {
       $("input[id*='id_upload_']").prop("checked", this.checked);
  });

  // Create Action
  $(".js-create-action").click(loadForm);
  $("#modal-item").on("submit", ".js-action-create-form", saveForm);

  // Edit Action
  $("#action-index").on("click", ".js-action-update", loadForm);
  $("#modal-item").on("submit", ".js-action-update-form", saveForm);

  // Delete Action
  $("#action-index").on("click", ".js-action-delete", loadForm);
  $("#modal-item").on("submit", ".js-action-delete-form", saveForm);

  // Clone Action
  $("#action-index").on("click", ".js-action-clone", loadForm);
  $("#modal-item").on("submit", ".js-action-clone-form", saveForm);

  // Edit Action Description
  $("#action-in-editor").on("click", ".js-description-edit", loadForm);
  $("#modal-item").on("submit", ".js-description-edit-form", saveForm);

  // Set view as filter
  $("#view-as-filter-selector").on("click", ".js-set-view-as-filter", loadForm);
  // View edit (when in the filter tab)
  $("#filter-set").on("click", ".js-view-edit", loadForm);
  $("#modal-item").on("submit", ".js-view-edit-form", saveForm);

  // Insert column name in content
  $("#insert-elements-in-editor").on("click", ".js-insert-column-name", insertAttributeInContent);
  // Insert column REPORT in content
  $("#insert-elements-in-editor").on("click", ".js-table-select", loadForm);
  $("#modal-item").on("click", ".js-table-insert", insertColumnListInContent);
  // Insert condition blurb in the editor
  $("#insert-elements-in-editor").on("click", ".js-insert-condition-name", insertConditionInContent);
  // Insert attribute in content
  $("#insert-elements-in-editor").on("click", ".js-insert-attribute-name", insertAttributeInContent);
  // Insert rubric feedback text in content
  $("#insert-elements-in-editor").on("click", ".js-insert-rubric-text", insertRubricTextInContent);

  // Insert columns in action in
  $("#insert-questions").on("click", ".js-insert-question", ajaxSimplePost);
  $("#column-selected-table").on("click", ".js-action-question-delete", ajaxSimplePost);

  // Insert columns in action in
  $("#edit-survey-tab-content").on("click", ".js-select-key-column-name", ajaxSimplePost);

  // Insert columns in action in
  $("#edit-survey-tab-content").on("click", ".js-select-condition", ajaxSimplePost);

  // Toggle shuffle question
  $("#action-in-editor").on("change", "#toggle-checkbox", toggleCheckBox);

  // Changes allowed in quewtion
  $("#action-in-editor").on("change", ".toggle-checkbox", toggleCheckBox);

  // Show stats
  $("#column-stat-selector").on("click", ".js-show-stats", loadForm);
  $("#rubric").on("click", ".js-show-stats", loadForm);

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
  $("#action-index").on("click", ".js-action-preview", loadForm);

  // Show URL
  $("#action-index").on("click", ".js-action-showurl", loadForm);
  $("#modal-item").on("submit", ".js-action-showurl-form", saveForm);

  // Column Add
  $("#edit-survey-tab-content").on("click", ".js-action-question-add", loadForm);
  $("#edit-survey-tab-content").on("click", ".js-action-todoitem-add", loadForm);
  $("#insert-criterion").on("click", ".js-workflow-criterion-insert", ajaxSimplePost);
  $("#insert-criterion").on("click", ".js-workflow-criterion-add", loadForm);
  $("#modal-item").on("submit", ".js-action-question-add-form", saveForm);
  $("#modal-item").on("submit", ".js-action-todoitem-add-form", saveForm);
  $("#modal-item").on("submit", ".js-workflow-criterion-add-form", saveForm);

  // Column Selected Edit
  $("#column-selected-table").on("click",
    ".js-action-question-edit",
    loadForm);
  $("#modal-item").on("submit", ".js-question-edit-form", saveForm);
  $("#modal-item").on("submit", ".js-todoitem-edit-form", saveForm);

  // Attachment operations
  $("#attachment-selector").on("click", ".js-attachment-insert", ajaxSimplePost);
  $("#attachment-set").on("click", ".js-attachment-delete", ajaxSimplePost);

  // Rubric operations
  $("#rubric").on("click", ".js-criterion-edit", loadForm);
  $("#modal-item").on("submit", ".js-criterion-edit-form", saveForm);
  $("#rubric").on("click", ".js-criterion-remove", loadForm);
  $("#modal-item").on("submit", ".js-criterion-remove-form", saveForm);
  $("#rubric").on("click", ".js-rubric-cell-edit", loadForm);
  $("#modal-item").on("submit", ".js-rubric-cell-create-form", saveForm);

  // Delete column
  $("#column-selected-table").on("click", ".js-column-delete", loadForm);

  // Clone column
  $("#column-selected-table").on("click", ".js-column-clone", loadForm);
  $("#modal-item").on("submit", ".js-column-clone-form", saveForm);

  // Flush workflow in detail view
  $("#action-index").on("click", ".js-workflow-flush", loadForm);
  $("#modal-item").on("submit", ".js-workflow-flush-form", saveForm);

  $(".ontask-ccard:not(.nohover), .ontask-acard:not(.nohover)").hover(function(){
    $(this).css("background-color", "lightgray");
  }, function(){
    $(this).css("background-color", "white");
  });
  $("#id_confirm_items").on("change", function(e) {
    select_next_button($(this));
  })
  $('#modal-item').on('shown.bs.modal', function (e) {
    if (typeof tinyMCE != 'undefined' && document.getElementById('id_description_text')) {
      tinyMCE.init({selector: 'textarea#id_description_text'});
    }
    if (typeof tinyMCE != 'undefined' && document.getElementById('id_feedback_text')) {
      tinyMCE.init({selector: 'textarea#id_feedback_text'});
    }
  });
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
  $(document.body).on("click", "a[data-bs-toggle]", function(event) {
    location.hash = this.getAttribute("href");
  });
  select_next_button($("#id_confirm_items"));
  $("#action-show-display").change(function(){
    $(this).find("option:selected").each(function(){
      var optionValue = $(this).attr("value");
      $(".ontask-acard").hide();
      if (optionValue) {
        $("div." + optionValue).show(300);
      } else {
        $(".ontask-acard").show(300);
      }
    })
  });
});
$(window).on("popstate", function() {
  let anchor = location.hash || $("a[data-bs-toggle='tab']").first().attr("href");
  $("a[href='" + anchor + "']").tab("show");
});
