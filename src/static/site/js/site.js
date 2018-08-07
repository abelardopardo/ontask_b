var set_qbuilder = function (element_id, qbuilder_options) {
    id_formula_value = $(element_id).val();
    if (id_formula_value != "null" && id_formula_value != "{}") {
      qbuilder_options['rules'] = JSON.parse(id_formula_value);
    }
    $('#builder').queryBuilder(qbuilder_options);
};
var set_column_select = function(element_id) {
  $(element_id).searchableOptionList({
    maxHeight: '250px',
    showSelectAll: true,
    texts: {
      searchplaceholder: gettext('Click here to search for columns'),
      noItemsAvailable: gettext('No columns found'),
    },
  });
 }
var insert_fields = function (the_form) {
    if (document.getElementById("id_filter") != null) {
      formula = $('#builder').queryBuilder('getRules');
      if (formula == null || !formula['valid']) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $('#id_filter').val(f_text);
    }
    return true;
}
var loadForm = function () {
    var btn = $(this);
    if ($(this).is('[class*="disabled"]')) {
      return;
    }
    data = {};
    if (document.getElementById("id_subject") != null) {
      data['subject_content'] = $("#id_subject").val();
    }
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      data: data,
      beforeSend: function() {
        $("#modal-item .modal-body").html("");
        $("#modal-item").modal("show");
      },
      success: function(data) {
        if (data.form_is_valid) {
          if (data.html_redirect == "") {
            window.location.reload(true);
          } else {
            location.href = data.html_redirect;
          }
          return;
        }
        $("#modal-item .modal-content").html(data.html_form);
        if (document.getElementById("id_formula") != null) {
          set_qbuilder('#id_formula', qbuilder_options);
        }
        if (document.getElementById("id_columns") != null) {
          set_column_select("#id_columns");
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
}
var saveForm = function () {
    var form = $(this);
    if (document.getElementById("id_formula") != null) {
      formula = $('#builder').queryBuilder('getRules');
      if (formula == null || !formula['valid']) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $('#id_formula').val(f_text);
    }
    var data = form.serializeArray();
    if (document.getElementById("id_content") != null) {
      data.push({'name': 'action_content',
                 'value': $("#id_content").summernote('code')});
    }
    $.ajax({
      url: form.attr("action"),
      data: data,
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          if (data.html_redirect == "") {
            window.location.reload(true);
          } else {
            location.href = data.html_redirect;
          }
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
          if (document.getElementById("id_formula") != null) {
            set_qbuilder('#id_formula', qbuilder_options);
          }
          if (document.getElementById("id_columns") != null) {
            set_column_select("#id_columns");
          }
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        location.reload();
      }
    });
    return false;
}
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip({
      trigger: "hover",
      placement: "auto",
      container: "body"
    });

});
$(window).bind("load", function() {
   $('#div-spinner').hide();
});

