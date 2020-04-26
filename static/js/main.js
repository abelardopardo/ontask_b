let previousActiveElement = null;
let dtp_opts = {
    format:'YYYY-MM-DD HH:mm',
    stepping: 1,
    toolbarPlacement: 'top',
    showTodayButton: true,
    showClear: true,
    showClose: true,
    sideBySide: true};
let set_qbuilder = function (element_id, qbuilder_options) {
    let id_formula_value = $(element_id).val();
    if (id_formula_value != "null" && id_formula_value != "{}") {
      qbuilder_options["rules"] = JSON.parse(id_formula_value);
    }
    $("#builder").queryBuilder(qbuilder_options);
};
let set_element_select = function(element_id) {
  $(element_id).searchableOptionList({
    maxHeight: "250px",
    showSelectAll: true,
    texts: {
      searchplaceholder: gettext("Click here to search"),
      noItemsAvailable: gettext("No element found")
    }
  });
 };
let insert_fields = function (the_form) {
    if (document.getElementById("id_filter") != null) {
      formula = $("#builder").queryBuilder("getRules");
      if (formula == null || !formula["valid"]) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $("#id_filter").val(f_text);
    }
    return true;
};
let get_id_text_content = function() {
  if (typeof $("#id_text_content").summernote != "undefined") {
    value = $("#id_text_content").summernote("code");
  } else {
    value = $("#id_text_content").val();
  }
  return value;
};
let loadForm = function () {
  let btn = $(this);
  previousActiveElement = btn;
  if (btn.is("[class*='dropdown-item']")) {
    previousActiveElement =  btn.parent().siblings()[0];
  }
  if ($(this).is("[class*='disabled']")) {
    return;
  }
  data = {};
  if (document.getElementById("id_subject") != null) {
    data["subject_content"] = $("#id_subject").val();
  }
  $.ajax({
    url: btn.attr("data-url"),
    type: "get",
    dataType: "json",
    data: data,
    beforeSend: function() {
      $("#modal-item .modal-body").html("");
      $("#modal-item").modal("show");
    },
    success: function(data) {
      if (typeof data.html_redirect != 'undefined') {
        if (data.html_redirect == "") {
          $("#div-spinner").show();
          window.location.reload(true);
        } else {
          location.href = data.html_redirect;
        }
        return;
      }
      $("#modal-item .modal-content").html(data.html_form);
      if ($('#modal-item .ontask-datetimepicker').length != 0) {
        $('#modal-item .ontask-datetimepicker').datetimepicker(dtp_opts);
      }
      if (document.getElementById("id_formula") != null) {
        set_qbuilder('#id_formula', qbuilder_options);
      }
      if (document.getElementById("id_columns") != null) {
        set_element_select("#id_columns");
      }
      $("#modal_item_label .close").focus();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $("#div-spinner").show();
      location.reload(true);
    }
  });
};
let saveForm = function () {
    let form = $(this);
    if (document.getElementById("id_formula") != null) {
      formula = $("#builder").queryBuilder('getRules');
      if (formula == null || !formula['valid']) {
        return false;
      }
      f_text = JSON.stringify(formula, undefined, 2);
      $("#id_formula").val(f_text);
    }
    let data = form.serializeArray();
    if (document.getElementById("id_text_content") != null) {
      value = get_id_text_content();
      data.push({"name": "action_content", "value": value});
    }
    $("#modal-item .modal-content").html("");
    $.ajax({
      url: form.attr("action"),
      data: data,
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (typeof data.html_redirect != 'undefined') {
          if (data.html_redirect == "") {
            $('#div-spinner').show();
            window.location.reload(true);
          } else if (data.html_redirect != null) {
            location.href = data.html_redirect;
          } else {
            $("#modal-item").modal('hide');
          }
        }
        else {
          $("#modal-item .modal-content").html(data.html_form);
          if (document.getElementById("id_formula") != null) {
            set_qbuilder('#id_formula', qbuilder_options);
          }
          if (document.getElementById("id_columns") != null) {
            set_element_select("#id_columns");
          }
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        $('#div-spinner').show();
        location.reload(true);
      }
    });
    return false;
};
let setDateTimePickers = function() {
  if ($('.ontask-datetimepicker').length != 0) {
    $('.ontask-datetimepicker').datetimepicker(dtp_opts);
  }
};
let assignColumn = function () {
  $('#div-spinner').show();
  let data = []
  if (document.getElementById("id_text_content") != null) {
    value = get_id_text_content();
    data.push({"name": "action_content", "value": value});
  }
  $.ajax({
    url: $(this).attr('data-url'),
    type: 'post',
    data: data,
    dataType: 'json',
    success: function (data) {
      if (typeof data.html_redirect != 'undefined') {
        if (data.html_redirect == "") {
          $('#div-spinner').show();
          window.location.reload(true);
        } else {
          location.href = data.html_redirect;
        }
      } else {
        $('#div-spinner').hide();
      }
      // Remove option from menu
      $(this).remove();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      location.reload(true);
    }
  });
}
let select_next_button = function(e) {
  if (e.is('input')) {
    val = !e.is(":checked");
  } else if (e.is('select')) {
    val = e.val() == '';
  } else {
    return;
  }
  $("#step_sequence").prop('hidden', val);
  $("#next-step-on").prop('hidden', val);
  $("#next-step-off").prop('hidden', !val);
}
let toggleCheckBox = function () {
  elem = $(this);
  $('#div-spinner').show();
  $.ajax({
    url: $(this).attr("data-url"),
    type: 'get',
    dataType: 'json',
    success: function (data) {
        if (data.is_checked == true) {
            elem.prop("checked", true)
        } else {
            elem.prop("checked", false)
        }
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $('#div-spinner').show();
      location.reload(true);
    }
  });
  $('#div-spinner').hide();
}
let toggleStar = function () {
  elem = $(this);
  $('#div-spinner').show();
  $.ajax({
    url: $(this).attr("data-url"),
    type: 'get',
    dataType: 'json',
    data: [],
    success: function (data) {
      $('#div-spinner').show();
      window.location.reload(true);
    },
    error: function(jqXHR, textStatus, errorThrown) {
      $('#div-spinner').show();
      location.reload(true);
    }
  });
  $('#div-spinner').hide();
}
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip({
    trigger: "hover",
    placement: "auto",
    container: "body",
    boundary: 'window',
  });
  $("body").on("click", ".spin", function () {
    $('#div-spinner').show();
  });
});
$(window).bind("pageshow", function() {
   $('#div-spinner').hide();
});
$(':input').on('invalid', function(e){
  $('#div-spinner').hide();
});
$('#modal-item').on('hide.bs.modal', function (e) {
  $("#modal-item .modal-content").html("");
  if (typeof qbuilder_options != 'undefined') {
    delete qbuilder_options['rules'];
  }
})
$('#modal-item').on('shown.bs.modal', function () {
  $("#modal_item_label .close").focus();
})
$('#modal-item').on('hidden.bs.modal', function (e) {
  if (previousActiveElement != 'undefined' && previousActiveElement != "null") {
      previousActiveElement.focus();
  }
})
// Detect workflow name before operation
$(document).on("keyup", '.textEnable', function() {
  $(".button-enable").prop( "disabled", $(this).val() != $(this).attr('data-value'));
});
$(function () {
  // Flush workflow
  $(".js-workflow-flush").on("click", loadForm);
  $("#modal-item").on("submit", ".js-workflow-flush-form", saveForm);
})

